from rest_framework.routers import DefaultRouter
from django.urls import include, path
from api.views import (
    IngredientsViewSet, RecipesViewSet, UsersViewSet,
    AddAndDeleteSubscribe, AuthToken, AddDeleteFavoriteRecipe,
    AddDeleteShoppingCart, IngredientsViewSet,
    RecipesViewSet, set_password, TagsViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipesViewSet)
router.register('ingredients', IngredientsViewSet)
router.register('users', UsersViewSet)
router.register('tags', TagsViewSet)

api_urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', AddDeleteFavoriteRecipe.as_view(), name='favorite_recipe'),
    path('users/<int:user_id>/subscribe/', AddAndDeleteSubscribe.as_view(), name='subscribe'),
    path('recipes/<int:recipe_id>/shopping_cart/', AddDeleteShoppingCart.as_view(), name='shopping_cart'),
    path('users/set_password/', set_password, name='set_password'),
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]

urlpatterns = [
    path('', include(api_urlpatterns)),
]
