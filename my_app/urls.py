from django.urls import path

from .views import book_list, home_page

urlpatterns = [
    path("", home_page, name="home"),
    path("book_list", book_list, name="book_list"),
]
