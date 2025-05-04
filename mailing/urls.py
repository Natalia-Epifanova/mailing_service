from django.urls import path
from django.views.decorators.cache import cache_page

from mailing.apps import MailingConfig
from mailing.views import RecipientCreateView, RecipientUpdateView, RecipientDetailView, RecipientDeleteView

app_name = MailingConfig.name

urlpatterns = [
    path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipient/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"
    ),
    path(
        "recipient_detail/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail",
    ),
    path(
        "recipient/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"
    ),
]