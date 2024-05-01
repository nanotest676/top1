from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=254,
        unique=True,
    )
    
    class Meta:
        ordering = ['id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email

class Subscribe(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        related_name='subscriptions',
        verbose_name="Subscriber",
        on_delete=models.CASCADE,
    )
    
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribers',
        verbose_name="Author",
        on_delete=models.CASCADE,
    )
    
    class Meta:
        ordering = ['-id']
        constraints = [
            UniqueConstraint(fields=['subscriber', 'author'], name='unique_subscription')
        ]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
