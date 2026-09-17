from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),  # Исправлено на urls
    path("", include("my_app.urls")),
]
