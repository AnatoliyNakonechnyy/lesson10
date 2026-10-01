from django.shortcuts import render

from ..models import Book


def book_list(request):
    """Renders a list of books."""
    books = Book.objects.select_related("category").all()
    context = {
        "books": books,
    }
    return render(request, "my_app/book_list.html", context)
