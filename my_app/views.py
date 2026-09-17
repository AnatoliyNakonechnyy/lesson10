from django.shortcuts import render

from .models import Book, Category


def home_page(request):

    categories = Category.objects.all()
    books = Book.objects.select_related("category").all()

    context = {
        "books": books,
        "categories": categories,
    }

    return render(request, "my_app/home_page.html", context)
