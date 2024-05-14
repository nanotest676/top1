from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth import get_user_model

from .models import User, Follow

User = get_user_model()


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email',)


class UserAdmin(ImportExportModelAdmin):
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
    list_filter = ('date_joined', 'email', 'first_name',)
    empty_value_display = '-пусто-'


class FollowResource(resources.ModelResource):
    class Meta:
        model = Follow
        fields = ('id', 'user', 'author',)


class FollowAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user', 'author',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)