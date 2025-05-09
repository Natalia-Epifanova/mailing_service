
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


from django.urls import reverse_lazy
from django.utils import timezone

from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)


from mailing.forms import DispatchForm, MessageForm, RecipientForm
from mailing.models import Dispatch, MailingAttempt, Message, Recipient


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user

    def handle_no_permission(self):
        from django.shortcuts import redirect

        return redirect("mailing:home")


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_dispatches"] = Dispatch.objects.count()

        context["active_dispatches"] = Dispatch.objects.filter(status="started").count()

        context["unique_recipients"] = Recipient.objects.count()

        return context


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDetailView(OwnerRequiredMixin, DetailView):
    model = Recipient


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
        return Recipient.objects.filter(owner=self.request.user)


class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing/messages_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(OwnerRequiredMixin, DetailView):
    model = Message


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
        return Dispatch.objects.filter(owner=self.request.user)


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


class DispatchDetailView(OwnerRequiredMixin, DetailView):
    model = Dispatch


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
