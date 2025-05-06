from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from users.apps import UsersConfig
from users.views import UserCreateView, edit_profile, email_verification

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(), name="register"),
    path("edit_profile/", edit_profile, name="edit_profile"),
    path("email_confirm/<str:token>/", email_verification, name="email_confirm"),
]
