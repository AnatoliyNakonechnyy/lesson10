from decimal import Decimal

from django.conf import settings
from django.http import HttpRequest

from .models import Book


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        """Initialize the cart using Django sessions."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # Save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    def add(
        self, book: Book, quantity: int = 1, override_quantity: bool = False
    ) -> None:
        """Add a book to the cart or update its quantity."""
        book_id = str(book.id)

        if book_id not in self.cart:
            self.cart[book_id] = {
                "quantity": 0,
                "price": str(
                    book.price
                ),  # Decimal converted to string for JSON serialization
            }

        if override_quantity:
            self.cart[book_id]["quantity"] = quantity
        else:
            self.cart[book_id]["quantity"] += quantity

        self.save()

    def remove(self, book: Book) -> None:
        """Remove a book from the cart."""
        book_id = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def clear(self) -> None:
        """Remove the cart from session."""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self) -> None:
        """Mark the session as modified to ensure it gets saved."""
        self.session.modified = True

    def __iter__(self):
        """Iterate over the items in the cart and get the books from the database."""
        book_ids = self.cart.keys()
        # Fetch book instances from DB
        books = Book.objects.filter(id__in=book_ids)

        cart_copy = self.cart.copy()
        for book in books:
            cart_copy[str(book.id)]["book"] = book

        for item in cart_copy.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self) -> int:
        """Count all items in the cart."""
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """Calculate the total cost of all items in the cart."""
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )
