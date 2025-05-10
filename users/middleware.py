from django.shortcuts import redirect
from django.urls import reverse


class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated and
                request.user.is_blocked and
                request.path != reverse('users:login')):
            from django.contrib.auth import logout
            logout(request)
            return redirect(reverse('users:login') + '?blocked=true')

        return self.get_response(request)