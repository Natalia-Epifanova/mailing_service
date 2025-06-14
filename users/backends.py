from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class CustomAuthBackend(ModelBackend):
    """
    Кастомный бэкенд аутентификации с проверкой блокировки пользователя.
    Наследуется от стандартного ModelBackend и добавляет проверку,
    не заблокирован ли пользователь перед аутентификацией.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Аутентифицирует пользователя с проверкой блокировки.
        Args:
            request (HttpRequest): Объект HTTP запроса.
            username (str, optional): Имя пользователя для аутентификации.
            password (str, optional): Пароль пользователя.
            **kwargs: Дополнительные аргументы.
        Returns:
            User: Аутентифицированный пользователь, если успешно и не заблокирован.
            None: Если аутентификация не удалась или пользователь заблокирован.
        """
        user = super().authenticate(request, username, password, **kwargs)
        if user and user.is_blocked:
            return None
        return user
