from django.forms import ModelForm

from mailing.models import Message, Recipient, Dispatch


class RecipientForm(ModelForm):
    class Meta:
        model = Recipient
        fields = "__all__"


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = "__all__"


class DispatchForm(ModelForm):
    class Meta:
        model = Dispatch
        exclude = ("first_sending_datetime", "end_of_sending_datetime")
