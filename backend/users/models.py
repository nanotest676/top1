from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username', #надо подправить
        'first_name', #надо подправить
        'last_name', #надо подправить
    ]
    email = models.EmailField(
        'email address', #надо подправить
        max_length=254,
        unique=True,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь' #надо подправить
        verbose_name_plural = 'Пользователи' #надо подправить

    def __str__(self):
        return self.username
