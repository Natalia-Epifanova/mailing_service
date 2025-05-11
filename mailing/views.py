import logging
from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from mailing.forms import DispatchForm, MessageForm, RecipientForm
from mailing.models import Dispatch, MailingAttempt, Message, Recipient
from mailing.services import (get_dispatches_for_user_from_cache,
                              get_dispatches_from_cache,
                              get_messages_for_user_from_cache,
                              get_messages_from_cache,
                              get_recipients_for_user_from_cache,
                              get_recipients_from_cache,
                              get_mailing_attempts_from_cache,
                              get_mailing_attempts_for_user_from_cache)
from users.models import User

logger = logging.getLogger('mailing')

class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """ Миксин для проверки доступа """
    request: HttpRequest
    def test_func(self):
        obj = self.get_object()
        user = self.request.user

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
        if self.request.user.is_authenticated:
            messages.error(self.request, "У вас нет прав для просмотра этой страницы")
            logger.warning(f"Unauthorized access attempt by {self.request.user}")
        return redirect("mailing:home")


class HomeView(TemplateView):
    """ Представление для отображения главной страницы"""
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
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
    """ Представление для добавления нового получателя"""
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        logger.info(f"Recipient created by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(f"Invalid recipient form submission by {self.request.user}: {form.errors}")
        return super().form_invalid(form)


class RecipientDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    """ Представление для просмотра информации о получателе"""
    model = Recipient
    permission_required = ["mailing.can_view_recipient_detail"]


class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
    """ Представление для редактирования получателя"""
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        logger.info(f"Recipient updated by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(f"Invalid recipient update by {self.request.user}: {form.errors}")
        return super().form_invalid(form)


class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
    """ Представление для удаления получателя"""
    model = Recipient
    success_url = reverse_lazy("mailing:recipients_list")

    def delete(self, request, *args, **kwargs):
        logger.info(f"Recipient deleted by {request.user}: {self.get_object()}")
        return super().delete(request, *args, **kwargs)


class RecipientListView(LoginRequiredMixin, ListView):
    """ Представление для просмотра списка получателей"""
    model = Recipient
    template_name = "mailing/recipients_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_recipients"):
            logger.debug(f"Loading all recipients for {user}")
            return get_recipients_from_cache()
        else:
            logger.debug(f"Loading user-specific recipients for {user}")
            return get_recipients_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Обработка неавторизованных пользователей"""
        if not request.user.is_authenticated:
            logger.warning("Anonymous user does not have access to view the page recipients_list")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class MessagesListView(LoginRequiredMixin, ListView):
    """ Представление для просмотра списка доступных сообщений"""
    model = Message
    template_name = "mailing/messages_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_messages"):
            logger.debug(f"Loading all messages for {user}")
            return get_messages_from_cache()
        else:
            logger.debug(f"Loading user-specific messages for {user}")
            return get_messages_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Обработка неавторизованных пользователей"""
        if not request.user.is_authenticated:
            logger.warning("Anonymous user does not have access to view the page messages_list")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class MessageCreateView(LoginRequiredMixin, CreateView):
    """ Представление для добавления нового сообщения"""
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        logger.info(f"Message created by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(f"Invalid message form submission by {self.request.user}: {form.errors}")
        return super().form_invalid(form)

class MessageDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    """ Представление для просмотра информации о сообщении"""
    model = Message
    permission_required = ["mailing.can_view_message_detail"]


class MessageUpdateView(OwnerRequiredMixin, UpdateView):
    """ Представление для редактирования сообщения"""
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")

    def form_valid(self, form):
        logger.info(f"Message updated by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(f"Invalid message update by {self.request.user}: {form.errors}")
        return super().form_invalid(form)


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
    """ Представление для удаления сообщения"""
    model = Message
    success_url = reverse_lazy("mailing:messages_list")

    def delete(self, request, *args, **kwargs):
        logger.info(f"Message deleted by {request.user}: {self.get_object()}")
        return super().delete(request, *args, **kwargs)


class DispatchesListView(LoginRequiredMixin, ListView):
    """ Представление для просмотра списка доступных рассылок"""
    model = Dispatch
    template_name = "mailing/dispatches_list.html"
    context_object_name = "dispatches"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_dispatches"):
            logger.debug(f"Loading all dispatches for {user}")
            return get_dispatches_from_cache()
        else:
            logger.debug(f"Loading user-specific dispatches for {user}")
            return get_dispatches_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Обработка неавторизованных пользователей"""
        if not request.user.is_authenticated:
            logger.warning("Anonymous user does not have access to view the page dispatches_list")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DispatchCreateView(LoginRequiredMixin, CreateView):
    """ Представление для добавления новой рассылки"""
    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")
    template_name = "mailing/dispatch_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["is_update"] = False
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        logger.info(f"Dispatch created by {self.request.user}: {form.instance}")
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.warning(f"Invalid dispatch form submission by {self.request.user}: {form.errors}")
        return super().form_invalid(form)


class DispatchDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    """ Представление для просмотра информации о рассылке"""
    model = Dispatch
    permission_required = ["mailing.can_view_dispatch_detail"]


class DispatchUpdateView(OwnerRequiredMixin, UpdateView):
    """ Представление для редактирования рассылки"""
    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")
    template_name = "mailing/dispatch_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        kwargs["is_update"] = True
        return kwargs

    def form_valid(self, form):
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
        logger.warning(f"Invalid dispatch form submission by {self.request.user}: {form.errors}")
        return super().form_invalid(form)


class DispatchDeleteView(OwnerRequiredMixin, DeleteView):
    """ Представление для удаления рассылки"""
    model = Dispatch
    success_url = reverse_lazy("mailing:dispatches_list")

    def delete(self, request, *args, **kwargs):
        logger.info(f"Dispatch deleted by {request.user}: {self.get_object()}")
        return super().delete(request, *args, **kwargs)


class DispatchStatsView(OwnerRequiredMixin, DetailView):
    """Представление для отображения статистики по рассылке"""
    model = Dispatch
    template_name = "mailing/dispatch_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dispatch = self.object

        try:
            attempts = MailingAttempt.objects.filter(dispatch=dispatch)

            context["total_attempts"] = attempts.count()
            context["success_attempts"] = attempts.filter(status="success").count()
            context["failed_attempts"] = attempts.filter(status="unsuccessfully").count()
            context["success_rate"] = (
                round((context["success_attempts"] / context["total_attempts"]) * 100, 2)
                if context["total_attempts"] > 0
                else 0
            )
            context["messages_sent"] = (
                    context["success_attempts"] * dispatch.recipient.count()
            )
            context["last_attempts"] = attempts.order_by("-mailing_attempt_datetime")[:5]

            logger.debug(f"Stats loaded for dispatch {dispatch.pk} by {self.request.user}")
        except Exception as e:
            logger.error(f"Error loading stats for dispatch {dispatch.pk}: {str(e)}")
            context["total_attempts"] = 0
            context["success_attempts"] = 0
            context["failed_attempts"] = 0
            context["success_rate"] = 0
            context["messages_sent"] = 0
            context["last_attempts"] = []

        return context


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempts_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_mailing_attempts"):
            logger.debug(f"Loading all mailing attempts for {user}")
            return get_mailing_attempts_from_cache()
        else:
            logger.debug(f"Loading user-specific mailing attempts for {user}")
            return get_mailing_attempts_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Обработка неавторизованных пользователей"""
        if not request.user.is_authenticated:
            logger.warning("Anonymous user does not have access to view the page mailing_attempts_list")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class FinishDispatchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "mailing.can_finish_dispatches"


    @staticmethod
    def post(request, pk):
        dispatch = get_object_or_404(Dispatch, pk=pk)
        dispatch.status = "completed"
        dispatch.save()
        logger.info(f"Dispatch {pk} finished by {request.user}")
        messages.success(request, f'Рассылка "{dispatch.message.theme}" остановлена.')
        return redirect(reverse("mailing:dispatches_list"))
