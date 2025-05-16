from django.shortcuts import redirect
from django.urls import reverse


class BlockedUserMiddleware:
    """
    Middleware для проверки блокировки пользователя во время запросов.
    Проверяет, не заблокирован ли аутентифицированный пользователь.
    Если пользователь заблокирован - разлогинивает его и перенаправляет
    на страницу входа с параметром blocked=true.
    """

    def __init__(self, get_response):
        """
        Инициализация middleware.
        Args:
            get_response (callable): Следующий middleware/представление в цепочке.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Обработка каждого входящего запроса.
        Args:
            request (HttpRequest): Входящий HTTP запрос.
        Returns:
            HttpResponse: Ответ на запрос или перенаправление для заблокированных пользователей.
        """
        if (
            request.user.is_authenticated
            and request.user.is_blocked
            and request.path != reverse("users:login")
        ):
            from django.contrib.auth import logout

            logout(request)
            return redirect(reverse("users:login") + "?blocked=true")

        return self.get_response(request)
