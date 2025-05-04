from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    email = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Email получателя",
    )
    full_name = models.CharField(
        max_length=100,
        verbose_name="ФИО получателя",
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий",
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"

    def __str__(self):
        return self.email


class Message(models.Model):
    theme = models.CharField(
        max_length=100,
        verbose_name="Тема письма",
    )
    content = models.TextField(
        blank=True,
        null=True,
        verbose_name="Тело письма",
    )

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"

    def __str__(self):
        return self.theme


class Dispatch(models.Model):
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    first_sending_datetime = models.DateTimeField(
        verbose_name="Дата и время первой отправки",
        blank=True,
        null=True,
    )
    end_of_sending_datetime = models.DateTimeField(
        verbose_name="Дата и время окончания отправки",
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="created",
        verbose_name="Статус отправки",
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.SET_NULL,
        verbose_name="Сообщение",
        null=True,
    )
    recipient = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["status", "end_of_sending_datetime"]

    def save(self, *args, **kwargs):
        """Устанавливаем дату первой отправки при изменении статуса на "Запущена"
        и дату окончания отправки при изменении статуса на "Завершена" """
        if self.status == "started" and not self.first_sending_datetime:
            self.first_sending_datetime = timezone.now()

        if self.status == "completed" and not self.end_of_sending_datetime:
            self.end_of_sending_datetime = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.message} - {self.status}"
