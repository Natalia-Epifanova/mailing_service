from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import UserRegisterForm, UserProfileForm
from users.models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")


@login_required
def edit_profile(request):
    user = request.user
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect(
                "mailing:home"
            )
    else:
        form = UserProfileForm(instance=user)

    return render(request, "users/edit_profile.html", {"form": form})

