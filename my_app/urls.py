from django.urls import path

from .views.book_list import (
    AsyncBookDeleteView,
    AsyncBookDetailView,
    AsyncBookListView,
    BookCreateView,
    BookUpdateView,
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
)
from .views.cart import cart_add, cart_detail, cart_remove
from .views.home_page import HomePageView
from .views.order import order_create, payment_cancel, payment_success, stripe_webhook

app_name = "store"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomLoginView.as_view(), name="login"),
    path("auth/logout/", CustomLogoutView.as_view(), name="logout"),
    path("books/", AsyncBookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", AsyncBookDetailView.as_view(), name="book_detail"),
    path("books/add/", BookCreateView.as_view(), name="book_create"),
    path("books/<int:pk>/edit/", BookUpdateView.as_view(), name="book_update"),
    path("books/<int:pk>/delete/", AsyncBookDeleteView.as_view(), name="book_delete"),
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:book_id>/", cart_add, name="cart_add"),
    path("cart/remove/<int:book_id>/", cart_remove, name="cart_remove"),
    path("order/create/", order_create, name="order_create"),
    path("order/success/", payment_success, name="payment_success"),
    path("order/cancel/", payment_cancel, name="payment_cancel"),
    path("webhook/stripe/", stripe_webhook, name="stripe_webhook"),
]
