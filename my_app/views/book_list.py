from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from my_app.models import Book


class BookListView(ListView):
    model = Book
    template_name = "my_app/book_list.html"
    context_object_name = "books"
    paginate_by = 6  # Пагінація по 6 книг

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            # Пошук за назвою або автором
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


class BookCreateView(CreateView):
    model = Book
    # Перераховуємо точні назви полів з вашої моделі Book
    fields = ("title", "author", "price", "description", "stock", "category")
    template_name = "my_app/book_form.html"
    success_url = reverse_lazy("store:book_list")


class BookUpdateView(UpdateView):
    model = Book
    # Ті самі поля для форми редагування
    fields = ("title", "author", "price", "description", "stock", "category")
    template_name = "my_app/book_form.html"
    success_url = reverse_lazy("store:book_list")


class BookDeleteView(DeleteView):
    model = Book
    template_name = "my_app/book_confirm_delete.html"
    success_url = reverse_lazy("store:book_list")
