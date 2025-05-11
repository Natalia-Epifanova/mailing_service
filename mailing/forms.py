from django import forms
from django.forms import ModelForm

from mailing.models import Dispatch, Message, Recipient
from mailing.services import (get_messages_for_user_from_cache,
                              get_messages_from_cache,
                              get_recipients_for_user_from_cache,
                              get_recipients_from_cache)


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class RecipientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and not instance.pk:
            instance.owner = self.request.user
        if commit:
            instance.save()
        return instance


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ["theme", "content"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request and not instance.pk:
            instance.owner = self.request.user
        if commit:
            instance.save()
        return instance


class DispatchForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Dispatch
        exclude = ("first_sending_datetime", "end_of_sending_datetime", "owner")

    def __init__(self, *args, **kwargs):
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
        instance = super().save(commit=False)
        if self.request:
            instance.owner = self.request.user
            if not instance.pk:
                instance.status = "created"
        if commit:
            instance.save()
            self.save_m2m()
        return instance
