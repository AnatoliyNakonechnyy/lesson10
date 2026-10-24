from django.http import HttpRequest

from .cart import Cart


def cart(request: HttpRequest) -> dict:
    """Return the cart instance to templates globally."""
    return {"cart": Cart(request)}
