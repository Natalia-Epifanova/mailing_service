from django.core.management.base import BaseCommand
from mailing.models import Dispatch

class Command(BaseCommand):
    help = 'Отправка рассылки по ID'

    def add_arguments(self, parser):
        parser.add_argument('dispatch_id', type=int, help='ID рассылки для отправки')

    def handle(self, *args, **kwargs):
        dispatch_id = kwargs['dispatch_id']
        try:
            dispatch = Dispatch.objects.get(id=dispatch_id)

            if dispatch.status == "started":
                dispatch.send_mail()
                self.stdout.write(self.style.SUCCESS(f'Рассылка с ID {dispatch_id} успешно отправлена.'))
            else:
                self.stdout.write(self.style.WARNING(f'Рассылка с ID {dispatch_id} не запущена. Статус: {dispatch.status}.'))
        except Dispatch.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Рассылка с ID {dispatch_id} не найдена.'))