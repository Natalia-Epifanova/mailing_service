import logging

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from mailing.forms import DispatchForm, MessageForm, RecipientForm
from mailing.models import Dispatch, MailingAttempt, Message, Recipient
from mailing.services import (
    get_dispatches_for_user_from_cache,
    get_dispatches_from_cache,
    get_mailing_attempts_for_user_from_cache,
    get_mailing_attempts_from_cache,
    get_messages_for_user_from_cache,
    get_messages_from_cache,
    get_recipients_for_user_from_cache,
    get_recipients_from_cache,
)

logger = logging.getLogger("mailing")


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Миксин для проверки прав доступа к объекту на основе владения.
    Проверяет, является ли пользователь владельцем объекта или имеет специальные права.
    Суперпользователи получают доступ автоматически.
    Attributes:
        request (HttpRequest): Объект HTTP запроса.
    """

    request: HttpRequest

    def test_func(self):
        """
        Проверяет, имеет ли текущий пользователь доступ к объекту.
        Returns:
            bool: True, если доступ разрешен, иначе False.
        """
        obj = self.get_object()
        user = self.request.user
        if user.is_superuser:
            logger.debug(f"Superuser {user} bypassed ownership check for {obj}")
            return True
        if hasattr(self, "permission_required"):
            for perm in self.permission_required:
                if user.has_perm(perm):
                    logger.debug(f"User {user} has permission {perm} for {obj}")
                    return True

        if obj.owner == user:
            logger.debug(f"User {user} is owner of {obj}")
            return True

        logger.warning(f"Access denied for user {user} to {obj}")
        return False

    def handle_no_permission(self):
        """
        Обрабатывает случай, когда доступ запрещен.
        Отправляет сообщение об ошибке и перенаправляет пользователя на главную страницу.
        """
        if self.request.user.is_authenticated:
            messages.error(self.request, "У вас нет прав для просмотра этой страницы")
            logger.warning(f"Unauthorized access attempt by {self.request.user}")
        return redirect("mailing:home")


class HomeView(TemplateView):
    """
    Главная страница приложения с отображением статистики рассылок.
    Показывает различную статистику в зависимости от роли пользователя:
    - Для менеджеров и суперпользователей: общая статистика по всем рассылкам
    - Для обычных пользователей: статистика только по их рассылкам
    - Для анонимных пользователей: базовая информация
    Attributes:
        template_name (str): Путь к шаблону страницы.
    """

    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        """
        Добавляет статистические данные в контекст шаблона.
        Returns:
            dict: Контекст с данными для отображения в шаблоне:
                - total_dispatches: Общее количество рассылок
                - active_dispatches: Количество активных рассылок
                - unique_recipients: Количество уникальных получателей
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            if user.is_authenticated:
                if user.is_superuser or user.groups.filter(name="Менеджеры").exists():
                    context["total_dispatches"] = Dispatch.objects.count()
                    context["active_dispatches"] = Dispatch.objects.filter(
                        status="started"
                    ).count()
                    context["unique_recipients"] = Recipient.objects.count()
                    logger.debug(f"Manager stats loaded for {user}")
                else:
                    context["total_dispatches"] = Dispatch.objects.filter(
                        owner=user
                    ).count()
                    context["active_dispatches"] = Dispatch.objects.filter(
                        owner=user, status="started"
                    ).count()
                    context["unique_recipients"] = Recipient.objects.filter(
                        owner=user
                    ).count()
                    logger.debug(f"User stats loaded for {user}")
            else:
                context["total_dispatches"] = 0
                context["active_dispatches"] = 0
                context["unique_recipients"] = 0
                logger.debug("Anonymous user accessed home page")
        except Exception as e:
            logger.error(f"Error loading home page stats: {str(e)}")
            context["total_dispatches"] = 0
            context["active_dispatches"] = 0
            context["unique_recipients"] = 0

        return context


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового получателя рассылки.
    Attributes:
        model (Model): Модель Recipient.
        form_class (Form): Класс формы RecipientForm.
        success_url (str): URL для перенаправления после успешного создания.
    """

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        """
        Обрабатывает валидную форму, устанавливая владельца получателя.
        Args:
            form (RecipientForm): Валидная форма получателя.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        form.instance.owner = self.request.user
        logger.info(f"Recipient created by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Логирует ошибки при невалидной форме.
        Args:
            form (RecipientForm): Невалидная форма получателя.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.warning(
            f"Invalid recipient form submission by {self.request.user}: {form.errors}"
        )
        return super().form_invalid(form)


class RecipientDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    """
    Представление для просмотра деталей получателя.
    Требует специального разрешения или прав владельца.
    Attributes:
        model (Model): Модель Recipient.
        permission_required (list): Список необходимых разрешений.
    """

    model = Recipient
    permission_required = ["mailing.can_view_recipient_detail"]

    def has_permission(self):
        """
        Проверяет наличие разрешений у пользователя.
        Returns:
            bool: True, если доступ разрешен, иначе False.
        """
        return self.request.user.is_superuser or super().has_permission()


class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
    """
    Представление для обновления данных получателя.
    Доступно только владельцу или суперпользователю.
    Attributes:
        model (Model): Модель Recipient.
        form_class (Form): Класс формы RecipientForm.
        success_url (str): URL для перенаправления после успешного обновления.
    """

    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        """
        Обрабатывает валидную форму обновления получателя.
        Args:
            form (RecipientForm): Валидная форма получателя.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.info(f"Recipient updated by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Логирует ошибки при невалидной форме обновления.
        Args:
            form (RecipientForm): Невалидная форма получателя.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.warning(
            f"Invalid recipient update by {self.request.user}: {form.errors}"
        )
        return super().form_invalid(form)

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или владелец.
        """
        return self.request.user.is_superuser or super().has_permission()


class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
    """
    Представление для удаления получателя.
    Attributes:
        model (Model): Модель Recipient.
        success_url (str): URL для перенаправления после удаления.
    """

    model = Recipient
    success_url = reverse_lazy("mailing:recipients_list")

    def delete(self, request, *args, **kwargs):
        """
        Логирует факт удаления получателя.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.info(f"Recipient deleted by {request.user}: {self.get_object()}")
        return super().delete(request, *args, **kwargs)

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или владелец.
        """
        return self.request.user.is_superuser or super().has_permission()


class RecipientListView(LoginRequiredMixin, ListView):
    """
    Представление для просмотра списка получателей рассылки.
    Наследуется от LoginRequiredMixin для проверки авторизации пользователя
    и от ListView для отображения списка объектов.
    Attributes:
        model (Model): Модель Recipient (Получатель), с которой работает представление.
        template_name (str): Путь к шаблону страницы списка получателей.
        context_object_name (str): Имя переменной контекста для списка получателей.
    """

    model = Recipient
    template_name = "mailing/recipients_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        """
        Возвращает queryset с получателями в зависимости от прав пользователя.
        Если пользователь имеет право can_view_all_recipients или является суперпользователем,
        возвращает всех получателей. В противном случае возвращает только получателей,
        связанных с текущим пользователем. Использует кэширование для получения данных.
        Returns:
            QuerySet: Список получателей в зависимости от прав пользователя.
        """
        user = self.request.user
        if user.has_perm("mailing.can_view_all_recipients") or user.is_superuser:
            logger.debug(f"Loading all recipients for {user}")
            return get_recipients_from_cache()
        else:
            logger.debug(f"Loading user-specific recipients for {user}")
            return get_recipients_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """
        Обрабатывает входящий запрос перед вызовом основного обработчика.
        Проверяет аутентификацию пользователя. Если пользователь не авторизован,
        логирует попытку доступа и перенаправляет на страницу авторизации.
        Args:
            request (HttpRequest): Входящий HTTP-запрос.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.
        Returns:
            HttpResponse: Ответ на запрос, либо перенаправление на страницу авторизации.
        """
        if not request.user.is_authenticated:
            logger.warning(
                "Anonymous user does not have access to view the page recipients_list"
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class MessagesListView(LoginRequiredMixin, ListView):
    """
    Представление для просмотра списка сообщений.
    Attributes:
        model (Model): Модель Message.
        template_name (str): Путь к шаблону.
        context_object_name (str): Имя переменной контекста.
    """

    model = Message
    template_name = "mailing/messages_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        """
        Возвращает queryset сообщений в зависимости от прав пользователя.
        Returns:
            QuerySet: Список сообщений.
        """
        user = self.request.user
        if user.has_perm("mailing.can_view_all_messages") or user.is_superuser:
            logger.debug(f"Loading all messages for {user}")
            return get_messages_from_cache()
        else:
            logger.debug(f"Loading user-specific messages for {user}")
            return get_messages_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет аутентификацию пользователя перед обработкой запроса.
        Args:
            request (HttpRequest): Входящий запрос.
        Returns:
            HttpResponse: Ответ или перенаправление для неаутентифицированных.
        """
        if not request.user.is_authenticated:
            logger.warning(
                "Anonymous user does not have access to view the page messages_list"
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового сообщения.
    Attributes:
        model (Model): Модель Message.
        form_class (Form): Класс формы MessageForm.
        success_url (str): URL для перенаправления после успешного создания.
    """

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")

    def form_valid(self, form):
        """
        Обрабатывает валидную форму, устанавливая владельца сообщения.
        Args:
            form (MessageForm): Валидная форма сообщения.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        form.instance.owner = self.request.user
        logger.info(f"Message created by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Логирует ошибки при невалидной форме.
        Args:
            form (MessageForm): Невалидная форма сообщения.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.warning(
            f"Invalid message form submission by {self.request.user}: {form.errors}"
        )
        return super().form_invalid(form)


class MessageDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    """
    Представление для просмотра деталей сообщения.
    Требует специального разрешения или прав владельца.
    Attributes:
        model (Model): Модель Message.
        permission_required (list): Список необходимых разрешений.
    """

    model = Message
    permission_required = ["mailing.can_view_message_detail"]

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или имеет права.
        """
        return self.request.user.is_superuser or super().has_permission()


class MessageUpdateView(OwnerRequiredMixin, UpdateView):
    """
    Представление для обновления сообщения.
    Доступно только владельцу или суперпользователю.
    Attributes:
        model (Model): Модель Message.
        form_class (Form): Класс формы MessageForm.
        success_url (str): URL для перенаправления после успешного обновления.
    """

    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")

    def form_valid(self, form):
        """
        Обрабатывает валидную форму обновления сообщения.
        Args:
            form (MessageForm): Валидная форма сообщения.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.info(f"Message updated by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Логирует ошибки при невалидной форме обновления.
        Args:
            form (MessageForm): Невалидная форма сообщения.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.warning(f"Invalid message update by {self.request.user}: {form.errors}")
        return super().form_invalid(form)

    def has_permission(self) -> bool:
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или владелец.
        """
        return self.request.user.is_superuser or super().has_permission()


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
    """
    Представление для удаления сообщения.
    Attributes:
        model (Model): Модель Message.
        success_url (str): URL для перенаправления после удаления.
    """

    model = Message
    success_url = reverse_lazy("mailing:messages_list")

    def delete(self, request, *args, **kwargs):
        """
        Логирует факт удаления сообщения.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.info(f"Message deleted by {request.user}: {self.get_object()}")
        return super().delete(request, *args, **kwargs)

    def has_permission(self) -> bool:
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или владелец.
        """
        return self.request.user.is_superuser or super().has_permission()


class DispatchesListView(LoginRequiredMixin, ListView):
    """
    Представление для просмотра списка рассылок.
    Отображает разные списки в зависимости от прав пользователя:
    - Все рассылки для суперпользователей и пользователей с правом can_view_all_dispatches
    - Только свои рассылки для обычных пользователей
    Attributes:
        model (Model): Модель Dispatch.
        template_name (str): Путь к шаблону.
        context_object_name (str): Имя переменной контекста.
    """

    model = Dispatch
    template_name = "mailing/dispatches_list.html"
    context_object_name = "dispatches"

    def get_queryset(self):
        """
        Возвращает queryset рассылок в зависимости от прав пользователя.
        Returns:
            QuerySet: Список рассылок.
        """
        user = self.request.user
        if user.has_perm("mailing.can_view_all_dispatches") or user.is_superuser:
            logger.debug(f"Loading all dispatches for {user}")
            return get_dispatches_from_cache()
        else:
            logger.debug(f"Loading user-specific dispatches for {user}")
            return get_dispatches_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет аутентификацию пользователя перед обработкой запроса.
        Args:
            request (HttpRequest): Входящий запрос.
        Returns:
            HttpResponse: Ответ или перенаправление для неаутентифицированных.
        """
        if not request.user.is_authenticated:
            logger.warning(
                "Anonymous user does not have access to view the page dispatches_list"
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DispatchCreateView(LoginRequiredMixin, CreateView):
    """
    Представление для создания новой рассылки.
    Attributes:
        model (Model): Модель Dispatch.
        form_class (Form): Класс формы DispatchForm.
        success_url (str): URL для перенаправления после успешного создания.
        template_name (str): Путь к шаблону формы.
    """

    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")
    template_name = "mailing/dispatch_form.html"

    def get_form_kwargs(self):
        """
        Добавляет дополнительные аргументы для формы.
        Returns:
            dict: Аргументы для формы, включая request и флаг is_update.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["is_update"] = False
        return kwargs

    def form_valid(self, form):
        """
        Обрабатывает валидную форму, устанавливая владельца рассылки.
        Args:
            form (DispatchForm): Валидная форма рассылки.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        form.instance.owner = self.request.user
        logger.info(f"Dispatch created by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Логирует ошибки при невалидной форме.
        Args:
            form (DispatchForm): Невалидная форма рассылки.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.warning(
            f"Invalid dispatch form submission by {self.request.user}: {form.errors}"
        )
        return super().form_invalid(form)

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или имеет права.
        """
        return self.request.user.is_superuser or super().has_permission()


class DispatchDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    """
    Представление для просмотра деталей рассылки.
    Требует специального разрешения или прав владельца.
    Attributes:
        model (Model): Модель Dispatch.
        permission_required (list): Список необходимых разрешений.
    """

    model = Dispatch
    permission_required = ["mailing.can_view_dispatch_detail"]

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или имеет права.
        """
        return self.request.user.is_superuser or super().has_permission()


class DispatchUpdateView(OwnerRequiredMixin, UpdateView):
    """
    Представление для обновления рассылки.
    При изменении статуса на "started" автоматически запускает рассылку.
    Attributes:
        model (Model): Модель Dispatch.
        form_class (Form): Класс формы DispatchForm.
        success_url (str): URL для перенаправления после успешного обновления.
        template_name (str): Путь к шаблону формы.
    """

    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")
    template_name = "mailing/dispatch_form.html"

    def get_form_kwargs(self):
        """
        Добавляет дополнительные аргументы для формы.
        Returns:
            dict: Аргументы для формы, включая request и флаг is_update.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["is_update"] = True
        return kwargs

    def form_valid(self, form):
        """
        Обрабатывает валидную форму обновления рассылки.
        При изменении статуса на "started" устанавливает дату первой отправки
        и запускает рассылку.
        Args:
            form (DispatchForm): Валидная форма рассылки.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        dispatch = form.save(commit=False)
        old_status = (
            Dispatch.objects.get(pk=dispatch.pk).status if dispatch.pk else None
        )

        if dispatch.status == "started" and old_status != "started":
            dispatch.first_sending_datetime = timezone.now()
            dispatch.save()
            form.save_m2m()
            dispatch.send_emails()
            return super().form_valid(form)

        dispatch.save()
        form.save_m2m()
        logger.info(f"Dispatch created by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Логирует ошибки при невалидной форме обновления.
        Args:
            form (DispatchForm): Невалидная форма рассылки.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.warning(
            f"Invalid dispatch form submission by {self.request.user}: {form.errors}"
        )
        return super().form_invalid(form)

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или владелец.
        """
        return self.request.user.is_superuser or super().has_permission()


class DispatchDeleteView(OwnerRequiredMixin, DeleteView):
    """
    Представление для удаления рассылки.
    Attributes:
        model (Model): Модель Dispatch.
        success_url (str): URL для перенаправления после удаления.
    """

    model = Dispatch
    success_url = reverse_lazy("mailing:dispatches_list")

    def delete(self, request, *args, **kwargs):
        """
        Логирует факт удаления рассылки.
        Returns:
            HttpResponse: Результат работы родительского метода.
        """
        logger.info(f"Dispatch deleted by {request.user}: {self.get_object()}")
        return super().delete(request, *args, **kwargs)

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или владелец.
        """
        return self.request.user.is_superuser or super().has_permission()


class DispatchStatsView(OwnerRequiredMixin, DetailView):
    """
    Представление для просмотра статистики по рассылке.
    Показывает:
    - Общее количество попыток отправки
    - Количество успешных и неудачных попыток
    - Процент успешных отправок
    - Общее количество отправленных сообщений
    - Последние 5 попыток отправки
    Attributes:
        model (Model): Модель Dispatch.
        template_name (str): Путь к шаблону.
    """

    model = Dispatch
    template_name = "mailing/dispatch_stats.html"

    def get_context_data(self, **kwargs):
        """
        Добавляет статистические данные в контекст шаблона.
        Returns:
            dict: Контекст с данными для отображения в шаблоне:
                - total_attempts: Общее количество попыток
                - success_attempts: Количество успешных попыток
                - failed_attempts: Количество неудачных попыток
                - success_rate: Процент успешных попыток
                - messages_sent: Общее количество отправленных сообщений
                - last_attempts: Последние 5 попыток
        """
        context = super().get_context_data(**kwargs)
        dispatch = self.object

        try:
            attempts = MailingAttempt.objects.filter(dispatch=dispatch)

            context["total_attempts"] = attempts.count()
            context["success_attempts"] = attempts.filter(status="success").count()
            context["failed_attempts"] = attempts.filter(
                status="unsuccessfully"
            ).count()
            context["success_rate"] = (
                round(
                    (context["success_attempts"] / context["total_attempts"]) * 100, 2
                )
                if context["total_attempts"] > 0
                else 0
            )
            context["messages_sent"] = (
                context["success_attempts"] * dispatch.recipient.count()
            )
            context["last_attempts"] = attempts.order_by("-mailing_attempt_datetime")[
                :5
            ]

            logger.debug(
                f"Stats loaded for dispatch {dispatch.pk} by {self.request.user}"
            )
        except Exception as e:
            logger.error(f"Error loading stats for dispatch {dispatch.pk}: {str(e)}")
            context["total_attempts"] = 0
            context["success_attempts"] = 0
            context["failed_attempts"] = 0
            context["success_rate"] = 0
            context["messages_sent"] = 0
            context["last_attempts"] = []

        return context

    def has_permission(self):
        """
        Проверяет наличие прав у пользователя.
        Returns:
            bool: True если пользователь суперпользователь или владелец.
        """
        return self.request.user.is_superuser or super().has_permission()


class MailingAttemptListView(LoginRequiredMixin, ListView):
    """
    Представление для просмотра списка попыток отправки.
    Attributes:
        model (Model): Модель MailingAttempt.
        template_name (str): Путь к шаблону.
        context_object_name (str): Имя переменной контекста.
    """

    model = MailingAttempt
    template_name = "mailing/mailing_attempts_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        """
        Возвращает queryset попыток отправки в зависимости от прав пользователя.
        Returns:
            QuerySet: Список попыток отправки.
        """
        user = self.request.user
        if user.has_perm("mailing.can_view_all_mailing_attempts"):
            logger.debug(f"Loading all mailing attempts for {user}")
            return get_mailing_attempts_from_cache()
        else:
            logger.debug(f"Loading user-specific mailing attempts for {user}")
            return get_mailing_attempts_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """
        Проверяет аутентификацию пользователя перед обработкой запроса.
        Args:
            request (HttpRequest): Входящий запрос.
        Returns:
            HttpResponse: Ответ или перенаправление для неаутентифицированных.
        """
        if not request.user.is_authenticated:
            logger.warning(
                "Anonymous user does not have access to view the page mailing_attempts_list"
            )
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class FinishDispatchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """
    Представление для завершения активной рассылки.
    Требует специального разрешения.
    Attributes:
        permission_required (str): Необходимое разрешение.
    """

    permission_required = "mailing.can_finish_dispatches"

    @staticmethod
    def post(request, pk):
        """
        Обрабатывает POST запрос для завершения рассылки.
        Args:
            request (HttpRequest): Входящий запрос.
            pk (int): ID рассылки для завершения.
        Returns:
            HttpResponseRedirect: Перенаправление на список рассылок.
        """
        dispatch = get_object_or_404(Dispatch, pk=pk)
        dispatch.status = "completed"
        dispatch.save()
        logger.info(f"Dispatch {pk} finished by {request.user}")
        messages.success(request, f'Рассылка "{dispatch.message.theme}" остановлена.')
        return redirect(reverse("mailing:dispatches_list"))
