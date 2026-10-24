from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..cart import Cart
from ..models import Book


class CartAddBookForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 21)],
        coerce=int,
        label="Quantity",
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )


@require_POST
def cart_add(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    form = CartAddBookForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(book=book, quantity=cd["quantity"], override_quantity=cd["override"])
    return redirect("store:cart_detail")


@require_POST
def cart_remove(request, book_id):
    cart = Cart(request)
    book = get_object_or_404(Book, id=book_id)
    cart.remove(book)
    return redirect("store:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddBookForm(
            initial={"quantity": item["quantity"], "override": True}
        )
    return render(request, "my_app/cart_detail.html", {"cart": cart})
