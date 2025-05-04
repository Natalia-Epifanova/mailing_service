from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView

from mailing.forms import RecipientForm
from mailing.models import Recipient


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:home") # ---------------------------------


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:home") # ---------------------------------


class RecipientDetailView(DetailView):
    model = Recipient


class RecipientDeleteView(DeleteView):
    model = Recipient
    success_url = reverse_lazy("mailing:home")