from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создание пользователя с правами группы 'Менеджеры'"

    def handle(self, *args, **options):
        group_name = "Менеджеры"
        group, created = Group.objects.get_or_create(name=group_name)

        email = "manager@example.com"
        password = "managerpass"

        user = User.objects.create(email=email)
        user.set_password(password)
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.save()

        user.groups.add(group)
