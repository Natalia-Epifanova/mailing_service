from django.core.management.base import BaseCommand

from mailing.models import Dispatch


class Command(BaseCommand):
    """
    Команда для отправки конкретной рассылки по ID.
    Позволяет вручную запустить отправку рассылки, проверяя её статус.
    Требует указания ID существующей рассылки.
    Пример использования:
        python manage.py send_email 1
    """

    help = "Отправка рассылки по ID"

    def add_arguments(self, parser):
        """
        Добавляет аргументы для команды.
        Args:
            parser (ArgumentParser): Парсер аргументов командной строки.
        """
        parser.add_argument("dispatch_id", type=int, help="ID рассылки для отправки")

    def handle(self, *args, **kwargs):
        """
        Основной метод обработки команды.
        Args:
            dispatch_id (int): ID рассылки из аргументов командной строки
        Выводит:
            Результат выполнения операции в консоль с цветовым оформлением
        """
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
