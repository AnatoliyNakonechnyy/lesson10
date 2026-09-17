from django.db.models import Q
from django.shortcuts import render

from .models import Book, Category


def home_page(request):

    search_query = request.GET.get("search", "")

    books = Book.objects.select_related("category").all()
    categories = Category.objects.all()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query)
            | Q(author__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    context = {
        "books": books,
        "categories": categories,
        "search_query": search_query,
    }
    return render(request, "my_app/home_page.html", context)
