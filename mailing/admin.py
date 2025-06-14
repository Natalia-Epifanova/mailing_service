from django.contrib import admin

from .models import Message, Recipient


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Recipient.

    Attributes:
        list_display (tuple): Поля, отображаемые в списке объектов.
        search_fields (tuple): Поля, по которым выполняется поиск.
    """

    list_display = ("email", "full_name", "comment")
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Message.

    Attributes:
        list_display (tuple): Поля, отображаемые в списке объектов.
        search_fields (tuple): Поля, по которым выполняется поиск.
    """

    list_display = ("theme", "content")
    search_fields = ("theme",)
