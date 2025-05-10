from django.urls import path


from mailing.apps import MailingConfig
from mailing.views import (DispatchCreateView, DispatchDeleteView,
                           DispatchDetailView, DispatchesListView,
                           DispatchStatsView, DispatchUpdateView, HomeView,
                           MailingAttemptListView, MessageCreateView,
                           MessageDeleteView, MessageDetailView,
                           MessagesListView, MessageUpdateView,
                           RecipientCreateView, RecipientDeleteView,
                           RecipientDetailView, RecipientListView,
                           RecipientUpdateView, FinishDispatchView)

app_name = MailingConfig.name

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("recipients_list/", RecipientListView.as_view(), name="recipients_list"),
    path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipient/<int:pk>/update/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipient_detail/<int:pk>/",
        RecipientDetailView.as_view(),
        name="recipient_detail",
    ),
    path(
        "recipient/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path("messages_list/", MessagesListView.as_view(), name="messages_list"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path(
        "message_detail/<int:pk>/",
        MessageDetailView.as_view(),
        name="message_detail",
    ),
    path(
        "message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path("dispatches_list/", DispatchesListView.as_view(), name="dispatches_list"),
    path("dispatch/create/", DispatchCreateView.as_view(), name="dispatch_create"),
    path(
        "dispatch/<int:pk>/update/",
        DispatchUpdateView.as_view(),
        name="dispatch_update",
    ),
    path(
        "dispatch_detail/<int:pk>/",
        DispatchDetailView.as_view(),
        name="dispatch_detail",
    ),
    path(
        "dispatch/<int:pk>/delete/",
        DispatchDeleteView.as_view(),
        name="dispatch_delete",
    ),
    path(
        "mailing_attempts_list/",
        MailingAttemptListView.as_view(),
        name="mailing_attempts_list",
    ),
    path(
        "dispatch/<int:pk>/stats/", DispatchStatsView.as_view(), name="dispatch_stats"
    ),
    path('finish/<int:pk>/', FinishDispatchView.as_view(), name='finish_dispatch'),
]
