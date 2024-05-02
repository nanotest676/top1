from .views import CustomUserViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter


app_name = 'users'

router = DefaultRouter()

router.register('users', CustomUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
