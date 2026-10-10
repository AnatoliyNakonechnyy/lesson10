from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from my_app.forms import CustomUserCreationForm
from my_app.models import Book


class RegisterView(CreateView):
    """Class for user registration."""

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("store:login")
    template_name = "my_app/register.html"


class CustomLoginView(LoginView):
    """Class for user login."""

    template_name = "my_app/login.html"


class CustomLogoutView(LogoutView):
    """Class for user logout."""

    next_page = reverse_lazy("store:login")


class BookListView(ListView):
    model = Book
    template_name = "my_app/book_list.html"
    context_object_name = "books"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(author__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "")
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = "my_app/book_detail.html"
    context_object_name = "book"


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    fields = ("title", "author", "price", "description", "stock", "category")
    template_name = "my_app/book_form.html"
    success_url = reverse_lazy("store:book_list")
    login_url = "store:login"
    permission_required = "my_app.add_book"  # Тепер захищено на рівні прав


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ("title", "author", "price", "description", "stock", "category")
    template_name = "my_app/book_form.html"
    success_url = reverse_lazy("store:book_list")
    login_url = "store:login"
    permission_required = "my_app.change_book"


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = "my_app/book_confirm_delete.html"
    success_url = reverse_lazy("store:book_list")
    login_url = "store:login"
    permission_required = "my_app.delete_book"
