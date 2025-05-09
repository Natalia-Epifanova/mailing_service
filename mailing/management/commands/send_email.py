from django.core.management.base import BaseCommand

from mailing.models import Dispatch


class Command(BaseCommand):
    help = "Отправка рассылки по ID"

    def add_arguments(self, parser):
        parser.add_argument("dispatch_id", type=int, help="ID рассылки для отправки")

    def handle(self, *args, **kwargs):
        dispatch_id = kwargs["dispatch_id"]
        try:
            dispatch = Dispatch.objects.get(id=dispatch_id)

            if dispatch.status == "started":
                # Передаем None в качестве request, чтобы избежать сообщений
                success = dispatch.send_mail(request=None)
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Рассылка с ID {dispatch_id} успешно отправлена."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Ошибка при отправке рассылки с ID {dispatch_id}"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Рассылка с ID {dispatch_id} не запущена. Статус: {dispatch.status}."
                    )
                )
        except Dispatch.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Рассылка с ID {dispatch_id} не найдена.")
            )
