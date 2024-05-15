import django_filters
from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()

class IngredientFilter(filters.FilterSet):
    """Filter for ingredients by name, supporting both startswith and contains lookups."""
    name = filters.CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ['name']

    def filter_name(self, queryset, name, value):
        if not value:
            return queryset
        startswith_lookup = f'{name}__istartswith'
        contains_lookup = f'{name}__icontains'
        return queryset.filter(
            Q(**{startswith_lookup: value}) | Q(**{contains_lookup: value})
        ).annotate(
            is_start=ExpressionWrapper(
                Q(**{startswith_lookup: value}),
                output_field=BooleanField()
            )
        ).order_by('-is_start')

class RecipeFilter(filters.FilterSet):
    """Filter for recipes by tags, author, is_favorited and is_in_shopping_cart."""
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.NumberFilter(method='filter_by_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_by_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_by_favorited(self, queryset, name, value):
        if not value:
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        favorite_recipes = [recipe.pk for recipe in queryset if recipe.is_favorited(user) == bool(value)]
        return queryset.filter(pk__in=favorite_recipes) if favorite_recipes else queryset.none()

    def filter_by_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        user = self.request.user
        if user.is_anonymous:
            return queryset
        shopping_cart_recipes = [recipe.pk for recipe in queryset if recipe.is_in_shopping_cart(user) == bool(value)]
        return queryset.filter(pk__in=shopping_cart_recipes) if shopping_cart_recipes else queryset.none()

    def filter_queryset(self, queryset):
        tags = self.data.get('tags')
        if tags and tags == "__all__":
            return queryset
        if not tags:
            return Recipe.objects.none()
        return super().filter_queryset(queryset)
