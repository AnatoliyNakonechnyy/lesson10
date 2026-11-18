# my_app/api_views.py
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Category, Book, Order
from .cart import Cart
from .serializers import (
    CategorySerializer,
    BookSerializer,
    OrderSerializer,
    CartSerializer,
    CartItemSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsOwnerOrAdmin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("id")
    serializer_class = CategorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["name", "slug"]
    search_fields = ["name"]
    ordering_fields = ["id", "name"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("category").all().order_by("id")
    serializer_class = BookSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = {
        "category": ["exact"],
        "category__slug": ["exact"],
        "author": ["exact", "icontains"],
        "price": ["exact", "gte", "lte"],
        "stock": ["gte"],
    }
    search_fields = ["title", "author", "description"]
    ordering_fields = ["id", "price", "title", "stock"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "city"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.prefetch_related("items__book__category").all()
        return Order.objects.prefetch_related("items__book__category").filter(
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet для управління сесійним кошиком користувача.
    """

    permission_classes = [AllowAny]
    serializer_class = CartSerializer

    def _serialize_cart(self, cart: Cart) -> dict:
        items = list(cart)
        data = {
            "items": items,
            "total_items": len(cart),
            "total_price": cart.get_total_price(),
        }
        return CartSerializer(data).data

    @extend_schema(responses=CartSerializer)
    def list(self, request):
        """Отримати поточний вміст кошика."""
        cart = Cart(request)
        return Response(self._serialize_cart(cart), status=status.HTTP_200_OK)

    @extend_schema(request=CartItemSerializer, responses=CartSerializer)
    @action(detail=False, methods=["post"], url_path="add")
    def add_item(self, request):
        """Додати книгу до кошика або оновити її кількість."""
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book = serializer.validated_data["book_id"]
        quantity = serializer.validated_data.get("quantity", 1)
        override = serializer.validated_data.get("override_quantity", False)

        cart = Cart(request)
        cart.add(book=book, quantity=quantity, override_quantity=override)
        return Response(self._serialize_cart(cart), status=status.HTTP_200_OK)

    @extend_schema(responses=CartSerializer)
    @action(detail=False, methods=["post"], url_path="remove")
    def remove_item(self, request):
        """Видалити конкретну книгу з кошика за її book_id."""
        book_id = request.data.get("book_id")
        if not book_id:
            return Response(
                {"detail": "Поле 'book_id' є обов'язковим."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        book = get_object_or_404(Book, id=book_id)
        cart = Cart(request)
        cart.remove(book)
        return Response(self._serialize_cart(cart), status=status.HTTP_200_OK)

    @extend_schema(responses=CartSerializer)
    @action(detail=False, methods=["post"], url_path="clear")
    def clear_cart(self, request):
        """Повністю очистити кошик."""
        cart = Cart(request)
        cart.clear()
        return Response(self._serialize_cart(cart), status=status.HTTP_200_OK)
