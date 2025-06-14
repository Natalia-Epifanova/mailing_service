from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import (
    CustomLoginView,
    ToggleUserBlockView,
    UserCreateView,
    UserDetailView,
    UserListView,
    edit_profile,
    email_verification,
)

app_name = UsersConfig.name

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("edit_profile/", edit_profile, name="edit_profile"),
    path("email_confirm/<str:token>/", email_verification, name="email_confirm"),
    path(
        "profile_detail/<int:pk>/",
        UserDetailView.as_view(),
        name="profile_detail",
    ),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            subject_template_name="users/password_reset_subject.txt",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("users/", UserListView.as_view(), name="users_list"),
    path("toggle-block/<int:pk>/", ToggleUserBlockView.as_view(), name="toggle_block"),
]
