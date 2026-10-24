from typing import ClassVar

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from my_app.models import CustomUser

from .models import Order


class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "phone_number")


class CustomUserChangeForm(UserChangeForm):
    """Form for editing a user's profile."""

    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone_number", "bio")


class OrderCreateForm(forms.ModelForm):
    """Form for collecting customer shipping and contact details during checkout."""

    class Meta:
        model = Order
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "address",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+380..."}
            ),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
        }
