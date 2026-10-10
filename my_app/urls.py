from django.urls import path
from .views.book_list import (
    BookCreateView,
    BookDeleteView,
    BookDetailView,
    BookListView,
    BookUpdateView,
    RegisterView,
    CustomLoginView,
    CustomLogoutView,
)
from .views.home_page import HomePageView

app_name = "store"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("books/", BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/add/", BookCreateView.as_view(), name="book_create"),
    path("books/<int:pk>/edit/", BookUpdateView.as_view(), name="book_update"),
    path("books/<int:pk>/delete/", BookDeleteView.as_view(), name="book_delete"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomLoginView.as_view(), name="login"),
    path("auth/logout/", CustomLogoutView.as_view(), name="logout"),
]
