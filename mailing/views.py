from django.utils import timezone

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from config.settings import EMAIL_HOST_USER
from mailing.forms import MessageForm, RecipientForm, DispatchForm
from mailing.models import Message, Recipient, Dispatch, MailingAttempt


class HomeView(TemplateView):
    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_dispatches'] = Dispatch.objects.count()

        context['active_dispatches'] = Dispatch.objects.filter(status='started').count()

        context['unique_recipients'] = Recipient.objects.count()

        return context


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")


class RecipientDetailView(DetailView):
    model = Recipient


class RecipientListView(ListView):
    model = Recipient
    template_name = "mailing/recipients_list.html"
    context_object_name = "recipients"


class RecipientDeleteView(DeleteView):
    model = Recipient
    success_url = reverse_lazy("mailing:recipients_list")


class MessagesListView(ListView):
    model = Message
    template_name = "mailing/messages_list.html"
    context_object_name = "messages"


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list")


class MessageDetailView(DetailView):
    model = Message


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:messages_list")


class DispatchesListView(ListView):
    model = Dispatch
    template_name = "mailing/dispatches_list.html"
    context_object_name = "dispatches"


class DispatchCreateView(CreateView):
    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")

    def form_valid(self, form):
        dispatch = form.save(commit=False)
        dispatch.status = "created"
        dispatch.save()
        form.save_m2m()
        return super().form_valid(form)


class DispatchUpdateView(UpdateView):
    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")

    def form_valid(self, form):
        dispatch = form.save(commit=False)
        if dispatch.status == "started":
            dispatch.first_sending_datetime = timezone.now()
            dispatch.send_mail()
        dispatch.save()
        return super().form_valid(form)


class DispatchDetailView(DetailView):
    model = Dispatch


class DispatchDeleteView(DeleteView):
    model = Dispatch
    success_url = reverse_lazy("mailing:dispatches_list")


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = "mailing/mailing_attempts_list.html"
    context_object_name = "attempts"

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.groups.filter(name="Manager").exists():
    #         return MailingAttempt.objects.all()
    #     return MailingAttempt.objects.filter(mailing__owner=user.id)
    #
