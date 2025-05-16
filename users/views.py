import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from config.settings import EMAIL_HOST_USER
from mailing.models import Dispatch
from users.forms import UserProfileForm, UserRegisterForm
from users.models import User


class UserCreateView(CreateView):
    """
    Представление для регистрации нового пользователя с подтверждением по email.
    Attributes:
        model (User): Модель пользователя.
        form_class (Form): Класс формы UserRegisterForm.
        success_url (str): URL для перенаправления после успешной регистрации.
    """

    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        """
        Обрабатывает валидную форму регистрации.
        Создает пользователя, генерирует токен подтверждения,
        отправляет email с ссылкой для подтверждения.
        Args:
            form (UserRegisterForm): Валидная форма регистрации.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        host = self.request.get_host()
        user.token = token
        user.save()
        url = f"http://{host}/users/email_confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Добрый день! Для подтверждения почты перейдите по ссылке {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list={user.email},
        )

        messages.success(
            self.request,
            "На ваш email была отправлена ссылка для подтверждения. "
            "Пожалуйста, проверьте вашу почту (включая папку 'Спам').",
        )
        return super().form_valid(form)


class UserDetailView(DetailView):
    """
    Представление для просмотра профиля пользователя.
    Attributes:
        model (User): Модель пользователя.
        template_name (str): Путь к шаблону страницы профиля.
    """

    model = User
    template_name = "users/profile_detail.html"


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Представление для просмотра списка пользователей.
    Требует права can_view_users_list.
    Attributes:
        model (User): Модель пользователя.
        template_name (str): Путь к шаблону списка пользователей.
        permission_required (str): Необходимое разрешение.
        context_object_name (str): Имя переменной контекста.
    """

    model = User
    template_name = "users/users_list.html"
    permission_required = "users.can_view_users_list"
    context_object_name = "users"

    def get_queryset(self):
        """
        Возвращает queryset обычных пользователей (не персонала).
        Returns:
            QuerySet: Список пользователей с is_staff=False.
        """
        return User.objects.filter(is_staff=False)


class ToggleUserBlockView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Представление для блокировки/разблокировки пользователя.
    Требует права can_block_users. При блокировке также завершает
    все активные рассылки пользователя.
    """

    permission_required = "users.can_block_users"

    @staticmethod
    def post(self, request, pk):
        """
        Обрабатывает POST запрос для блокировки/разблокировки.
        Args:
            request (HttpRequest): Входящий запрос.
            pk (int): ID пользователя для блокировки/разблокировки.
        Returns:
            HttpResponseRedirect: Перенаправление на список пользователей.
        """
        user = get_object_or_404(User, pk=pk)
        user.is_blocked = not user.is_blocked
        user.save()

        if user.is_blocked:
            from django.contrib.auth import logout

            if request.user == user:
                logout(request)
            Dispatch.objects.filter(owner=user, status="started").update(
                status="completed"
            )
            if request.user == user:
                return redirect(reverse("users:login") + "?blocked=true")
            messages.success(request, f"Пользователь {user.email} заблокирован.")
        else:
            messages.success(request, f"Пользователь {user.email} разблокирован.")

        return redirect(reverse("users:users_list"))


def email_verification(request, token):
    """
    Подтверждение email пользователя по токену.
    Args:
        request (HttpRequest): Входящий запрос.
        token (str): Токен подтверждения из email.
    Returns:
        HttpResponseRedirect: Перенаправление на страницу входа.
    """
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = ""
    user.save()
    messages.success(
        request, "Ваш email успешно подтвержден! Теперь вы можете войти в систему."
    )
    return redirect(reverse("users:login"))


@login_required
def edit_profile(request):
    """
    Редактирование профиля пользователя.
    Args:
        request (HttpRequest): Входящий запрос.
    Returns:
        HttpResponse: Страница редактирования профиля или перенаправление на главную.
    """
    user = request.user
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("mailing:home")
    else:
        form = UserProfileForm(instance=user)

    return render(request, "users/edit_profile.html", {"form": form})


class CustomLoginView(LoginView):
    """
    Кастомное представление для входа с проверкой блокировки.
    Attributes:
        template_name (str): Путь к шаблону страницы входа.
    """

    template_name = "users/login.html"

    def form_invalid(self, form):
        """
        Обрабатывает невалидную форму входа с проверкой блокировки.
        Args:
            form (AuthenticationForm): Невалидная форма входа.
        Returns:
            HttpResponse: Страница входа с ошибками.
        """
        username = form.data.get("username")
        password = form.data.get("password")

        try:
            user = User.objects.get(email=username)
            if user.is_blocked:
                form.add_error(
                    None,
                    "blocked:Ваш аккаунт заблокирован. Обратитесь к администратору.",
                )
                return self.render_to_response(self.get_context_data(form=form))
        except User.DoesNotExist:
            pass

        return super().form_invalid(form)
