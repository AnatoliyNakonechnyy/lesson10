import math
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, View
from asgiref.sync import sync_to_async  # Нативна утиліта Django для потоків

from my_app.forms import CustomUserCreationForm
from my_app.models import Book
from .cart import CartAddBookForm


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


class AsyncBookListView(View):
    template_name = "my_app/book_list.html"
    paginate_by = 6

    async def get(self, request, *args, **kwargs):
        def render_sync():
            query = request.GET.get("q")
            queryset = Book.objects.all().order_by("id")

            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) | Q(author__icontains=query)
                )

            total_count = queryset.count()

            try:
                page_number = int(request.GET.get("page", 1))
            except ValueError:
                page_number = 1

            total_pages = math.ceil(total_count / self.paginate_by) or 1
            if page_number > total_pages:
                page_number = total_pages
            elif page_number < 1:
                page_number = 1

            offset = (page_number - 1) * self.paginate_by
            books_list = list(
                queryset[
                    offset : offset
                    + self.simulate_page_end(page_number, total_pages, total_count)
                ]
            )

            page_obj = {
                "has_next": page_number < total_pages,
                "has_previous": page_number > 1,
                "number": page_number,
                "next_page_number": page_number + 1,
                "previous_page_number": page_number - 1,
                "paginator": {"num_pages": total_pages},
            }

            context = {
                "books": books_list,
                "page_obj": page_obj,
                "is_paginated": total_pages > 1,
                "cart_product_form": CartAddBookForm(),
            }
            return render(request, self.template_name, context)

        return await sync_to_async(render_sync, thread_sensitive=True)()

    def simulate_page_end(self, page, total_pages, total_count):
        if page == total_pages:
            return total_count
        return page * self.paginate_by


class AsyncBookDetailView(View):
    template_name = "my_app/book_detail.html"

    async def get(self, request, pk, *args, **kwargs):
        def render_sync():
            try:
                book = Book.objects.get(pk=pk)
            except Book.DoesNotExist:
                return None
            return render(request, self.template_name, {"book": book})

        response = await sync_to_async(render_sync, thread_sensitive=True)()
        if response is None:
            raise Http404("Book not found")
        return response


class AsyncBookDeleteView(LoginRequiredMixin, View):
    template_name = "my_app/book_confirm_delete.html"
    success_url = reverse_lazy("store:book_list")
    login_url = "store:login"
    permission_required = "my_app.delete_book"

    async def get(self, request, pk, *args, **kwargs):
        def render_sync():
            if not request.user.has_perm(self.permission_required):
                return HttpResponseForbidden(
                    "You do not have permission to delete books."
                )
            try:
                book = Book.objects.get(pk=pk)
            except Book.DoesNotExist:
                return None
            return render(request, self.template_name, {"book": book})

        response = await sync_to_async(render_sync, thread_sensitive=True)()
        if response is None:
            raise Http404("Book not found")
        return response

    async def post(self, request, pk, *args, **kwargs):
        def process_delete_sync():
            if not request.user.has_perm(self.permission_required):
                return HttpResponseForbidden(
                    "You do not have permission to delete books."
                )
            try:
                book = Book.objects.get(pk=pk)
                book.delete()
                return redirect(self.success_url)
            except Book.DoesNotExist:
                return None

        response = await sync_to_async(process_delete_sync, thread_sensitive=True)()
        if response is None:
            raise Http404("Book not found")
        return response


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    fields = ("title", "author", "price", "description", "stock", "category")
    template_name = "my_app/book_form.html"
    success_url = reverse_lazy("store:book_list")
    login_url = "store:login"
    permission_required = "my_app.add_book"


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ("title", "author", "price", "description", "stock", "category")
    template_name = "my_app/book_form.html"
    success_url = reverse_lazy("store:book_list")
    login_url = "store:login"
    permission_required = "my_app.change_book"
