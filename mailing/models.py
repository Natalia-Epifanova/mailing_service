from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from users.models import User


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
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True
    )

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        permissions = [
            ("can_view_all_recipients", "Can view all recipients"),
            ("can_view_recipient_detail", "Can view recipient detail"),
        ]

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
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True
    )

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"
        permissions = [
            ("can_view_all_messages", "Can view all messages"),
            ("can_view_message_detail", "Can view message detail"),
        ]

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
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["status", "end_of_sending_datetime"]
        permissions = [
            ("can_view_all_dispatches", "Can view all dispatches"),
            ("can_view_dispatch_detail", "Can view dispatch detail"),
        ]

    def save(self, *args, **kwargs):
        """Устанавливаем дату первой отправки при изменении статуса на "Запущена"
        и дату окончания отправки при изменении статуса на "Завершена" """
        if self.status == "started":
            self.first_sending_datetime = timezone.now()
            self.send_emails()

        if self.status == "completed":
            self.end_of_sending_datetime = timezone.now()

        super().save(*args, **kwargs)

    def send_emails(self):
        """Отправка писем для всех получателей"""
        recipients = self.recipient.all()
        for recipient in recipients:
            try:
                send_mail(
                    subject=self.message.theme,
                    message=self.message.content,
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing_attempt_datetime=timezone.now(),
                    status="success",
                    dispatch=self,
                )
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing_attempt_datetime=timezone.now(),
                    status="unsuccessfully",
                    server_response=str(e),
                    dispatch=self,
                )

    def __str__(self):
        return f"{self.message} - {self.status}"


class MailingAttempt(models.Model):
    STATUS_CHOICES = [
        ("success", "Успешно"),
        ("unsuccessfully", "Не успешно"),
    ]
    mailing_attempt_datetime = models.DateTimeField(
        verbose_name="Дата и время попытки",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="unsuccessfully",
        verbose_name="Статус отправки",
    )
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ответ почтового сервера",
    )
    dispatch = models.ForeignKey(
        Dispatch,
        on_delete=models.SET_NULL,
        verbose_name="Рассылка",
        null=True,
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Владелец", blank=True, null=True
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        permissions = [
            ("can_view_all_mailing_attempts", "Can view all mailing attempts"),
        ]

