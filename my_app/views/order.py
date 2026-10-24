import json
import stripe
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from ..cart import Cart
from ..forms import OrderCreateForm
from my_app.models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


def order_created_email(order):
    """sends an email to the customer confirming the order."""
    subject = f"BookStore — Order #{order.id} Confirmed!"
    message = (
        f"Dear {order.first_name},\n\n"
        f"Thank you for your purchase! Your payment for order #{order.id} was successfully processed.\n\n"
        f"Order Details:\n"
        f"-------------------------\n"
    )
    for item in order.items.all():
        message += f"- {item.book.title} ({item.quantity}x) — {item.price} грн\n"
    message += (
        f"-------------------------\n"
        f"Total Cost: {order.get_total_cost()} грн\n\n"
        f"Delivery Address: {order.city}, {order.address}\n\n"
        f"Best regards,\nBookStore Team 📚"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=False,
    )


def order_create(request):
    """Creates an order and redirects to the Stripe payment page."""
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Your cart is empty!")
        return redirect("store:book_list")

    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.save()
                    line_items = []
                    for item in cart:
                        book = item["book"]
                        qty = item["quantity"]
                        if book.stock < qty:
                            raise ValueError(
                                f"Sorry, only {book.stock} pcs of '{book.title}' available."
                            )
                        book.stock -= qty
                        book.save()
                        OrderItem.objects.create(
                            order=order,
                            book=book,
                            price=item["price"],
                            quantity=qty,
                        )
                        line_items.append(
                            {
                                "price_data": {
                                    "currency": "uah",
                                    "product_data": {
                                        "name": book.title,
                                        "description": f"Author: {book.author}",
                                    },
                                    "unit_amount": int(item["price"] * 100),
                                },
                                "quantity": qty,
                            }
                        )
                    success_url = (
                        request.build_absolute_uri(reverse("store:payment_success"))
                        + f"?order_id={order.id}"
                    )
                    cancel_url = request.build_absolute_uri(
                        reverse("store:payment_cancel")
                    )

                    checkout_session = stripe.checkout.Session.create(
                        line_items=line_items,
                        mode="payment",
                        success_url=success_url,
                        cancel_url=cancel_url,
                        client_reference_id=str(order.id),
                        customer_email=order.email,
                    )
                    request.session["legacy_cart_total"] = str(cart.get_total_price())
                    cart.clear()
                    return redirect(checkout_session.url, code=303)

            except ValueError as e:
                print(f"❌ VALUE ERROR: {e}")
                messages.error(request, str(e))
                return redirect("store:cart_detail")
            except Exception as e:
                print(f"❌ STRIPE ERROR: {e}")
                messages.error(request, f"Stripe error: {str(e)}")
                return redirect("store:cart_detail")
        else:
            print(f"❌ FORM INVALID ERRORS: {form.errors.as_data()}")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": getattr(request.user, "phone_number", ""),
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, "my_app/order_create.html", {"cart": cart, "form": form})


def payment_success(request):
    """Handles the successful payment callback from Stripe. Updates the order status to 'paid' and sends a confirmation email to the customer."""
    order_id = request.GET.get("order_id")
    cart_total = request.session.pop("legacy_cart_total", "0.00")

    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if order.status != "paid":
                with transaction.atomic():
                    order = Order.objects.select_for_update().get(id=order_id)
                    if order.status != "paid":
                        order.status = "paid"
                        order.save()
                        order_created_email(order)
        except Order.DoesNotExist:
            order = None

    return render(
        request, "my_app/order_created.html", {"order": order, "cart_total": cart_total}
    )


def payment_cancel(request):
    """payment was canceled or failed. Redirects to the cart detail page with an error message."""
    messages.error(request, "Payment was canceled or failed. Please try again.")
    return redirect("store:cart_detail")


@csrf_exempt
def stripe_webhook(request):
    """Asynchronous webhook from Stripe for guaranteed payment confirmation."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session.get("client_reference_id")

        if order_id:
            try:
                mark_order_as_paid(order_id, session["id"])
            except Exception as e:
                print(f"❌ Помилка оновлення статусу замовлення в вебхуку: {e}")
                return HttpResponse(status=500)

    return HttpResponse(status=200)


def mark_order_as_paid(order_id, stripe_session_id):
    """safely and atomically update the order status."""
    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(id=order_id)
        except Order.DoesNotExist:
            print(f"❌ Замовлення #{order_id} не знайдено в базі даних.")
            return

        if order.status != "paid":
            order.status = "paid"
            if hasattr(order, "stripe_id"):
                order.stripe_id = stripe_session_id
            order.save()

            order_created_email(order)
            print(f"✅ Замовлення #{order.id} успішно оплачене через вебхук.")
