from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Subscribe
from rest_framework import status
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user, author=obj
        ).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class TagSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeReadSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    is_in_shopping_cart = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'is_in_shopping_cart',
            'is_favorited',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipe

    def get_ingredients(self, obj):
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = Recipe


class SubscribeSerializer(CustomUserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ('email', 'username',)

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if author == user:
            raise ValidationError(
                detail='Вы не можете подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(
            recipes,
            many=True,
            read_only=True
        )
        return serializer.data


class IngredientInRecipeWriteSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        fields = ('id', 'amount',)
        model = IngredientInRecipe


class RecipeWriteSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        model = Recipe

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен один и более ингридиент!'
            })
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингридиентов должно быть 1 и более!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'tags': 'Нужен хотя бы один тег!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError({'tags': 'Теги должны быть уникальными!'})
            tags_list.append(tag)
        return value

    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        self.create_ingredients_amounts(
            recipe=recipe,
            ingredients=ingredients
        )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance,
            ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(
            instance, context=context
        ).data
