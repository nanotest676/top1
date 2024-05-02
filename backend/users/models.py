from django.db.models import UniqueConstraint
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    email = models.EmailField(
        verbose_name='Email Address',
        unique=True,
        max_length=254,
    )

    class Meta:
        verbose_name = 'Пользователь'
        ordering = ['id']
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        verbose_name="Подписчик",
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscriptions',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(fields=['subscriber', 'author'], name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
