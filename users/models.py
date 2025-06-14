from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя с email в качестве идентификатора.
    Добавляет дополнительные поля и функциональность:
    - Аватар пользователя
    - Телефон
    - Страна
    - Токен для API
    - Флаг блокировки пользователя
    Attributes:
        email (EmailField): Уникальный email пользователя (используется как USERNAME_FIELD).
        avatar (ImageField): Аватар пользователя.
        phone (CharField): Номер телефона.
        country (CharField): Страна пользователя.
        token (CharField): Токен для API.
        is_blocked (BooleanField): Флаг блокировки пользователя.
    """

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
        """
        Мета-класс для дополнительных настроек модели.
        Attributes:
            verbose_name (str): Имя модели в единственном числе.
            verbose_name_plural (str): Имя модели во множественном числе.
            permissions (list): Кастомные разрешения для этой модели.
        """

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_users_list", "Can view users list"),
            ("can_block_users", "Can block/unblock users"),
            ("can_finish_dispatches", "Can finish dispatches"),
        ]

    def __str__(self):
        """
        Строковое представление пользователя.
        Returns:
            str: Email пользователя.
        """
        return self.email

    def is_active(self):
        """
        Проверяет, активен ли пользователь (не заблокирован).
        Переопределяет стандартный метод, учитывая флаг is_blocked.
        Returns:
            bool: True если пользователь активен и не заблокирован, иначе False.
        """
        return super().is_active and not self.is_blocked
