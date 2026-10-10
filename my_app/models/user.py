from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    called CustomUser to avoid confusion with the built-in User model.
    This model extends the default Django User model by adding additional fields.
    """

    bio = models.TextField("Bio", max_length=500, blank=True)
    phone_number = models.CharField("Phone Number", max_length=15, blank=True)

    class Meta:
        app_label = "my_app"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username
