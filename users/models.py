from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Фото",
    )

    phone = models.CharField(
        max_length=35,
        verbose_name="Телефон",
        blank=True,
        null=True,
    )
    country = models.CharField(
        max_length=35,
        verbose_name="Страна",
        blank=True,
        null=True,
    )
    token = models.CharField(
        max_length=100,
        verbose_name="Токен",
        blank=True,
        null=True,
    )

    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_users_list", "Can view users list"),
            ("can_block_users", "Can block/unblock users"),
            ("can_finish_dispatches", "Can finish dispatches"),
        ]

    def __str__(self):
        return self.email

    def is_active(self):
        """Переопределяем метод, чтобы заблокированные пользователи считались неактивными"""
        return super().is_active and not self.is_blocked
