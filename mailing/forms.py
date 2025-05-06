from django.forms import ModelForm

from mailing.models import Message, Recipient, Dispatch


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class RecipientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Recipient
        fields = "__all__"


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = "__all__"


class DispatchForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Dispatch
        exclude = ("first_sending_datetime", "end_of_sending_datetime")
