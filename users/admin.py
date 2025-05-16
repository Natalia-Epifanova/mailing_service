from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели User.
    Attributes:
        list_display (tuple): Поля, отображаемые в списке объектов.
    """

    list_display = ("id", "email")
