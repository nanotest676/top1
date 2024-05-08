from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from drf_base64.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, get_user_model


from recipes.models import Ingredient, Recipe, RecipeIngredient, Subscribe, Tag

User = get_user_model()


class GetIsSubscribedMixin:
    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            user.follower.filter(author=obj).exists()
            if user.is_authenticated
            else False
        )


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label='эмаил',
        write_only=True)
    token = serializers.CharField(
        label='токен',
        read_only=True)
    password = serializers.CharField(
        label='пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')
        if email and password:
            user = authenticate(
                email=email,
                request=self.context.get('request'),
                password=password
            )
            if not user:
                raise serializers.ValidationError(
                    'Не получилось авторизоваться',
                    code='authorization')
        else:
            text = 'Нужно добавить "почту" и "пароль".'
            raise serializers.ValidationError(
                text,
                code='authorization')
        attrs['user'] = user
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name', 'password',)

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class UserListSerializer(
        serializers.ModelSerializer,
        GetIsSubscribedMixin,
    ):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'id',
            'first_name', 'last_name', 'is_subscribed')



class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id', 'color', 'name', 'slug',)


class UserPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        label='Нынешний пароль')
    new_password = serializers.CharField(
        label='Новый пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                'Не получилось войти.', code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        password = make_password(
            validated_data.get('new_password'))
        user = self.context['request'].user
        user.password = password
        user.save()
        return validated_data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeUserSerializer(
        serializers.ModelSerializer,
        GetIsSubscribedMixin,
    ):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'id',
            'first_name', 'last_name', 'is_subscribed')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'amount', 'measurement_unit')


class IngredientsEditSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    id = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('amount', 'id')


class RecipeReadSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True)
    author = RecipeUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe')
    is_favorited = serializers.BooleanField(
        read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        use_url=True,
        max_length=None,
    )
    ingredients = IngredientsEditSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    

    class Meta:
        fields = '__all__'
        model = Recipe
        read_only_fields = ('author',)

    def validate(self, data):
        ingredient_list = []
        ingredients = data['ingredients']
        for items in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=items['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Необходим неиспользованный рецепт!')
            ingredient_list.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Минимум 1 тэг для рецепта!')
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга {tag_name} не существует!')
        return data

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте!')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1!')
        return ingredients

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1!')
        return cooking_time

    

    def create(self, validated_data):
        recipe = Recipe.objects.create(**validated_data)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient_id=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='author.id'
    )
    username = serializers.CharField(
        source='author.username'
    )
    email = serializers.EmailField(
        source='author.email'
    )
    last_name = serializers.CharField(
        source='author.last_name'
    )
    first_name = serializers.CharField(
        source='author.first_name'
    )
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True
    )
    is_subscribed = serializers.BooleanField(
        read_only=True
    )
    

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'recipes', 'is_subscribed', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipe_limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(recipe_limit)] if recipe_limit
            else obj.author.recipe.all()
        )
        return SubscribeRecipeSerializer(
            recipes,
            many=True
        ).data
