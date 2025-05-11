from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создание обычного пользователя"

    def handle(self, *args, **options):
        user = User.objects.create(email="user@example.com")
        user.set_password("userpass")
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.save()
