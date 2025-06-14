from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from mailing.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """
    Форма регистрации нового пользователя с email вместо username.
    Наследуется от стандартной UserCreationForm с добавлением стилей через StyleFormMixin.
    Attributes:
        model (User): Модель пользователя.
        fields (tuple): Поля формы - email и два поля для пароля.
    """

    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class UserProfileForm(StyleFormMixin, ModelForm):
    """
    Форма для редактирования профиля пользователя.
    Позволяет изменять аватар, телефон и страну пользователя.
    Attributes:
        model (User): Модель пользователя.
        fields (tuple): Поля формы - avatar, phone, country.
    """

    class Meta:
        model = User
        fields = ("avatar", "phone", "country")
