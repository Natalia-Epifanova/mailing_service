from django.apps import AppConfig


class MailingConfig(AppConfig):
    """
    Конфигурация приложения mailing.

    Attributes:
        default_auto_field (str): Тип авто-поля для моделей.
        name (str): Имя приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "mailing"
