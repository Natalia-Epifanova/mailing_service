from django.db import models

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
