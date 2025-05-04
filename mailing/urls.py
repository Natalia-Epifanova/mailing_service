from django.urls import path
from django.views.decorators.cache import cache_page

from mailing.apps import MailingConfig
from mailing.views import RecipientCreateView, RecipientUpdateView, RecipientDetailView, RecipientDeleteView, \
    RecipientListView, HomeView, MessagesListView, MessageCreateView, MessageUpdateView, MessageDetailView, \
    MessageDeleteView

app_name = MailingConfig.name

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("recipients_list/", RecipientListView.as_view(), name="recipients_list"),

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
    path("messages_list/", MessagesListView.as_view(), name="messages_list"),

    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "message_detail/<int:pk>/", MessageDetailView.as_view(), name="message_detail",
    ),
    path(
        "message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
]