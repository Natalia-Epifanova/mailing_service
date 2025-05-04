from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from mailing.forms import MessageForm, RecipientForm, DispatchForm
from mailing.models import Message, Recipient, Dispatch


class HomeView(TemplateView):
    template_name = "mailing/home.html"


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


class DispatchUpdateView(UpdateView):
    model = Dispatch
    form_class = DispatchForm
    success_url = reverse_lazy("mailing:dispatches_list")


class DispatchDetailView(DetailView):
    model = Dispatch


class DispatchDeleteView(DeleteView):
    model = Dispatch
    success_url = reverse_lazy("mailing:dispatches_list")
