from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Subscribe, User, Subscribe, User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("is_active", "username", "first_name", "last_name", "email")
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ['username']
    list_filter = ('is_active', 'first_name', 'email')
    save_on_top = True

@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription)