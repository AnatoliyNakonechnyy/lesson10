from django.http import HttpResponse

from .models import Book, Category


def home_page(request):

    books = Book.objects.all()
    categories = Category.objects.all()

    html_content = "<h1>List of Categories</h1><ul>"
    if not categories:
        html_content += "<li>No categories available. Add them in the admin panel!</li>"
    else:
        for category in categories:
            html_content += f"<li><strong>{category.name}</strong></li>"
    html_content += "</ul>"

    html_content += "<h1>List of Books</h1><ul>"
    if not books:
        html_content += "<li>No books available. Add them in the admin panel!</li>"
    else:
        for book in books:
            html_content += f"<li><strong>{book.title}</strong> — {book.price} usd. - {book.category.name}</li>"

    html_content += "</ul>"

    return HttpResponse(html_content)
