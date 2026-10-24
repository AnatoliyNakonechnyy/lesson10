from django.urls import path

from .views.book_list import (
    BookCreateView,
    BookDeleteView,
    BookDetailView,
    BookListView,
    BookUpdateView,
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
)
from .views.cart import cart_add, cart_detail, cart_remove
from .views.home_page import HomePageView
from .views.order import order_create, payment_success, payment_cancel, stripe_webhook


app_name = "store"

urlpatterns = [
    # Головна сторінка та авторизація
    path("", HomePageView.as_view(), name="home"),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomLoginView.as_view(), name="login"),
    path("auth/logout/", CustomLogoutView.as_view(), name="logout"),
    # Керування каталогом книг
    path("books/", BookListView.as_view(), name="book_list"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/add/", BookCreateView.as_view(), name="book_create"),
    path("books/<int:pk>/edit/", BookUpdateView.as_view(), name="book_update"),
    path("books/<int:pk>/delete/", BookDeleteView.as_view(), name="book_delete"),
    # Кошик (Session-based Cart)
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:book_id>/", cart_add, name="cart_add"),
    path("cart/remove/<int:book_id>/", cart_remove, name="cart_remove"),
    # ВИПРАВЛЕНО: Оформлення замовлення та Stripe Checkout
    path("order/create/", order_create, name="order_create"),
    path("order/success/", payment_success, name="payment_success"),
    path("order/cancel/", payment_cancel, name="payment_cancel"),
    path("webhook/stripe/", stripe_webhook, name="stripe_webhook"),
]
