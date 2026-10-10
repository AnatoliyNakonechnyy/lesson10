from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from my_app.forms import CustomUserCreationForm


class RegisterView(CreateView):
    """class for user registration."""

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"


class CustomLoginView(LoginView):
    """class for logging in."""

    template_name = "registration/login.html"


class CustomLogoutView(LogoutView):
    """class for logging out."""

    next_page = reverse_lazy("login")
