from django.contrib.auth import get_user_model
from django.contrib import admin


@admin.register(get_user_model())
class User(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'email',)
    search_fields = ('username', 'email',)
