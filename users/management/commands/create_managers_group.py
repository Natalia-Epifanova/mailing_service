from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Dispatch, Message, Recipient
from users.models import User


class Command(BaseCommand):
    help = 'Creates Managers group with permissions'

    def handle(self, *args, **options):
        managers_group, created = Group.objects.get_or_create(name='Менеджеры')

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Менеджеры" создана'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Менеджеры" уже существует'))

        permissions = [
            Permission.objects.get(codename='can_view_all_recipients'),
            Permission.objects.get(codename='can_view_all_messages'),
            Permission.objects.get(codename='can_view_all_dispatches'),
            Permission.objects.get(codename='can_view_users_list'),

            Permission.objects.get(codename='can_block_users'),
            Permission.objects.get(codename='can_finish_dispatches'),
        ]

        managers_group.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно добавлено {len(permissions)} разрешений для группы "Менеджеры"'
            )
        )