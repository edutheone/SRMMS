
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .access_control import AdminRequiredMixin
from .forms import (
    LoginForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard:index")

    return render(
        request,
        "accounts/login.html",
        {"form": form},
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def profile(request):
    return render(
        request,
        "accounts/profile.html",
    )


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 10

    def get_queryset(self):
        return User.objects.all().order_by("username")


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            f'User "{self.object.username}" was created successfully.',
        )

        return response


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        response = super().form_valid(form)

        messages.success(
            self.request,
            f'User "{self.object.username}" was updated successfully.',
        )

        return response
