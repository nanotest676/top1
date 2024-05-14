from django.urls import path, include

from backend.users.views import UsersViewSet


app_name = 'users'

urlpatterns = [
    path('users/', UsersViewSet),
    path('auth/', include('djoser.urls.authtoken')),
]
