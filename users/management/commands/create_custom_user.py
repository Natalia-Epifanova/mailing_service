from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """
    Команда для создания стандартного пользователя.
    Создает пользователя с предустановленными параметрами:
    - Email: user@example.com
    - Пароль: userpass
    - Без прав администратора
    Пример использования:
        python manage.py create_custom_user
    """

    help = "Создание обычного пользователя"

    def handle(self, *args, **options):
        """Создает и сохраняет пользователя в базе данных."""
        user = User.objects.create(email="user@example.com")
        user.set_password("userpass")
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.save()
