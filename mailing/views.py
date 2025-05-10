from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect

from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View

from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)


from mailing.forms import DispatchForm, MessageForm, RecipientForm
from mailing.models import Dispatch, MailingAttempt, Message, Recipient
from mailing.services import get_recipients_from_cache, get_recipients_for_user_from_cache, get_messages_from_cache, \
    get_messages_for_user_from_cache, get_dispatches_from_cache, get_dispatches_for_user_from_cache


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        user = self.request.user

        if hasattr(self, 'permission_required'):
            for perm in self.permission_required:
                if user.has_perm(perm):
                    return True
        return obj.owner == user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            from django.contrib import messages
            messages.error(self.request, "У вас нет прав для просмотра этой страницы")
        from django.shortcuts import redirect
        return redirect("mailing:home")


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name='Managers').exists():
                context["total_dispatches"] = Dispatch.objects.count()
                context["active_dispatches"] = Dispatch.objects.filter(status="started").count()
                context["unique_recipients"] = Recipient.objects.count()
            else:
                context["total_dispatches"] = Dispatch.objects.filter(owner=user).count()
                context["active_dispatches"] = Dispatch.objects.filter(owner=user, status="started").count()
                context["unique_recipients"] = Recipient.objects.filter(owner=user).count()
        else:
            context["total_dispatches"] = 0
            context["active_dispatches"] = 0
            context["unique_recipients"] = 0

        return context


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")


    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Recipient
    permission_required = ['mailing.can_view_recipient_detail']


class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")


class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy("mailing:recipients_list")


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/recipients_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_recipients"):
            return get_recipients_from_cache()
        else:
            return get_recipients_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Обработка неавторизованных пользователей"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)



class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/messages_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_messages"):
            return get_messages_from_cache()
        else:
            return get_messages_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Обработка неавторизованных пользователей"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Message
    permission_required = ['mailing.can_view_message_detail']

class MessageUpdateView(OwnerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:messages_list")


class DispatchesListView(LoginRequiredMixin, ListView):
    model = Dispatch
    template_name = "mailing/dispatches_list.html"
    context_object_name = "dispatches"

    def get_queryset(self):
        user = self.request.user
        if user.has_perm("mailing.can_view_all_dispatches"):
            return get_dispatches_from_cache()
        else:
            return get_dispatches_for_user_from_cache(self.request.user)

    def dispatch(self, request, *args, **kwargs):
        """Обработка неавторизованных пользователей"""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class DispatchCreateView(LoginRequiredMixin, CreateView):
    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")
    template_name = "mailing/dispatch_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['is_update'] = False  # Указываем, что это создание
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DispatchDetailView(PermissionRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Dispatch
    permission_required = ['mailing.can_view_dispatch_detail']


class DispatchUpdateView(OwnerRequiredMixin, UpdateView):
    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")
    template_name = "mailing/dispatch_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['is_update'] = True
        return kwargs

    def form_valid(self, form):
        dispatch = form.save(commit=False)
        old_status = Dispatch.objects.get(pk=dispatch.pk).status if dispatch.pk else None

        if dispatch.status == "started" and old_status != "started":
            dispatch.first_sending_datetime = timezone.now()
            dispatch.save()
            form.save_m2m()
            dispatch.send_emails()
            return super().form_valid(form)

        dispatch.save()
        form.save_m2m()
        return super().form_valid(form)


class DispatchDeleteView(OwnerRequiredMixin, DeleteView):
    model = Dispatch
    success_url = reverse_lazy("mailing:dispatches_list")


class DispatchStatsView(OwnerRequiredMixin, DetailView):
    model = Dispatch
    template_name = "mailing/dispatch_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dispatch = self.object
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

        return context


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempts_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        return MailingAttempt.objects.filter(dispatch__owner=self.request.user)


class FinishDispatchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'mailing.can_finish_dispatches'

    def post(self, request, pk):
        dispatch = get_object_or_404(Dispatch, pk=pk)
        dispatch.status = 'completed'
        dispatch.save()
        messages.success(request, f'Рассылка "{dispatch.message.theme}" остановлена.')
        return redirect(reverse('mailing:dispatches_list'))