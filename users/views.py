from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User

import secrets


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        host = self.request.get_host()
        user.token = token
        user.save()
        url = f"http://{host}/users/email_confirm/{token}/"
        send_mail(
            subject="Подтверждение почты",
            message=f"Добрый день! Для подтверждения почты перейдите по ссылке {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list={user.email},
        )
        return super().form_valid(form)


class UserDetailView(DetailView):
    model = User
    template_name = "users/profile_detail.html"


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = ""
    user.save()
    return redirect(reverse("users:login"))


@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("mailing:home")
    else:
        form = UserProfileForm(instance=user)

    return render(request, "users/edit_profile.html", {"form": form})
