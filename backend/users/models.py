from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    USER = 'user'
    ADMIN = 'admin'


class CustomUser(AbstractUser):
    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        help_text='Enter a unique username.'
    )
    email = models.EmailField(
        'Email Address',
        max_length=254,
        unique=True,
        help_text='Enter a valid email address.'
    )
    first_name = models.CharField('First Name', max_length=150)
    last_name = models.CharField('Last Name', max_length=150)
    role = models.CharField(
        'User Role',
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.USER,
        help_text='Select user role.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Follower'
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followings',
        verbose_name='Following'
    )

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.follower} follows {self.following}'
