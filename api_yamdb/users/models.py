from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.settings import ADMIN, MODERATOR, USER, USERNAME_MAX_LENGTH


ROLES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    role = models.CharField(
        choices=ROLES,
        default=USER,
        max_length=max(len(role) for role, role_verbose_name in ROLES)
    )
    bio = models.TextField(blank=True, null=True)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username
