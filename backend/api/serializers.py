from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import Follow
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data)
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'date_joined')


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    following = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('id', 'follower', 'following')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'amount']


class RecipeReadSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'author',
            'ingredients',
            'tags',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        ]


class RecipeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'ingredients',
            'tags',
            'image',
            'text',
            'cooking_time'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль введен неверно')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
