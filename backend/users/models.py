from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=254
    )
    
    class Meta:
        ordering = ['id',]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='subscribing',
        on_delete=models.CASCADE,
    )
    
    class Meta:
        ordering = ['-id',]
        constraints = [
            UniqueConstraint(
                name='unique_subscription',
                fields=['user', 'author']
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
