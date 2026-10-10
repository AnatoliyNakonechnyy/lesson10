from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from my_app.models import CustomUser


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
