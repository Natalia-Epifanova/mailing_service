from django import forms
from django.forms import ModelForm

from mailing.models import Dispatch, Message, Recipient
from mailing.services import (
    get_messages_for_user_from_cache,
    get_messages_from_cache,
    get_recipients_for_user_from_cache,
    get_recipients_from_cache,
)


class StyleFormMixin:
    """
    Миксин для стилизации форм. Добавляет CSS-класс 'form-control' ко всем полям формы.
    Methods:
        __init__: Инициализирует форму и добавляет CSS-классы ко всем полям.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class RecipientForm(StyleFormMixin, ModelForm):
    """
    Форма для создания и редактирования получателей рассылки.
    Attributes:
        model (Model): Модель Recipient, с которой работает форма.
        fields (list): Список полей, включаемых в форму.
    Methods:
        __init__: Инициализирует форму с учетом текущего запроса.
        save: Сохраняет экземпляр модели, устанавливая владельца для новых объектов.
    """

    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму с возможностью передачи request.
        Args:
            request (HttpRequest): Объект запроса для определения владельца.
        """
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Сохраняет объект получателя, устанавливая владельца при создании.
        Args:
            commit (bool): Определяет, нужно ли сохранять объект в БД.
        Returns:
            Recipient: Сохраненный или подготовленный к сохранению объект.
        """
        instance = super().save(commit=False)
        if self.request and not instance.pk:
            instance.owner = self.request.user
        if commit:
            instance.save()
        return instance


class MessageForm(StyleFormMixin, ModelForm):
    """
    Форма для создания и редактирования сообщений рассылки.
    Attributes:
        model (Model): Модель Message, с которой работает форма.
        fields (list): Список полей, включаемых в форму.
    Methods:
        __init__: Инициализирует форму с учетом текущего запроса.
        save: Сохраняет экземпляр модели, устанавливая владельца для новых объектов.
    """

    class Meta:
        model = Message
        fields = ["theme", "content"]

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму с возможностью передачи request.
        Args:
            request (HttpRequest): Объект запроса для определения владельца.
        """
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        """
        Сохраняет объект сообщения, устанавливая владельца при создании.
        Args:
            commit (bool): Определяет, нужно ли сохранять объект в БД.
        Returns:
            Message: Сохраненный или подготовленный к сохранению объект.
        """
        instance = super().save(commit=False)
        if self.request and not instance.pk:
            instance.owner = self.request.user
        if commit:
            instance.save()
        return instance


class DispatchForm(StyleFormMixin, ModelForm):
    """
    Форма для создания и редактирования рассылок.
    Attributes:
        model (Model): Модель Dispatch, с которой работает форма.
        exclude (tuple): Список исключаемых из формы полей.
    Methods:
        __init__: Инициализирует форму с учетом прав пользователя и режима редактирования.
        save: Сохраняет экземпляр рассылки, устанавливая владельца и начальный статус.
    """

    class Meta:
        model = Dispatch
        exclude = ("first_sending_datetime", "end_of_sending_datetime", "owner")

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму с учетом прав пользователя.
        Args:
            request (HttpRequest): Объект запроса для определения прав.
            is_update (bool): Флаг режима редактирования существующей рассылки.
        """
        self.request = kwargs.pop("request", None)
        is_update = kwargs.pop("is_update", False)
        super().__init__(*args, **kwargs)

        if self.request:
            if self.request.user.is_superuser:
                self.fields["message"].queryset = get_messages_from_cache()
            else:
                self.fields["message"].queryset = get_messages_for_user_from_cache(
                    self.request.user
                )

            # Для получателей
            if self.request.user.is_superuser:
                self.fields["recipient"].queryset = get_recipients_from_cache()
            else:
                self.fields["recipient"].queryset = get_recipients_for_user_from_cache(
                    self.request.user
                )

        if is_update:
            self.fields["status"].widget.attrs.update({"class": "form-control"})
        else:
            self.fields["status"].widget = forms.HiddenInput()
            self.fields["status"].initial = "created"

    def save(self, commit=True):
        """
        Сохраняет объект рассылки, устанавливая владельца и начальный статус.
        Args:
            commit (bool): Определяет, нужно ли сохранять объект в БД.
        Returns:
            Dispatch: Сохраненный или подготовленный к сохранению объект.
        """
        instance = super().save(commit=False)
        if self.request:
            instance.owner = self.request.user
            if not instance.pk:
                instance.status = "created"
        if commit:
            instance.save()
            self.save_m2m()
        return instance
