from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView, TemplateView

from mailing.forms import RecipientForm, MessageForm
from mailing.models import Recipient, Message


class HomeView(TemplateView):
    template_name = "mailing/home.html"

class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list")


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:recipients_list") # ---------------------------------


class RecipientDetailView(DetailView):
    model = Recipient

class RecipientListView(ListView):
    model = Recipient
    template_name = "mailing/recipients_list.html"
    context_object_name = 'recipients'


class RecipientDeleteView(DeleteView):
    model = Recipient
    success_url = reverse_lazy("mailing:recipients_list")


class MessagesListView(ListView):
    model = Message
    template_name = "mailing/messages_list.html"
    context_object_name = 'messages'

class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list") # ---------------------------------


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:messages_list") # ---------------------------------


class MessageDetailView(DetailView):
    model = Message


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy("mailing:messages_list")