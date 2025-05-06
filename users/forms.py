from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from mailing.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class UserProfileForm(StyleFormMixin, ModelForm):
    class Meta:
        model = User
        fields = ("avatar", "phone", "country")


