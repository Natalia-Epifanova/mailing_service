from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурация приложения users.

    Attributes:
        default_auto_field (str): Тип авто-поля для моделей.
        name (str): Имя приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
