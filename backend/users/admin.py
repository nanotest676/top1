from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'username',
        'email'
    )
    list_filter = ('first_name', 'email')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
