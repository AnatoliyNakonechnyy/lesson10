# my_app/serializers.py
from rest_framework import serializers
from .models import Category, Book, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "price",
            "description",
            "stock",
            "category",
            "category_id",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source="book",
        write_only=True,
    )
    cost = serializers.DecimalField(
        source="get_cost", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ["id", "book", "book_id", "price", "quantity", "cost"]
        read_only_fields = ["price", "cost"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    user = serializers.ReadOnlyField(source="user.username")
    total_cost = serializers.DecimalField(
        source="get_total_cost", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "status",
            "created_at",
            "updated_at",
            "total_cost",
            "items",
        ]
        read_only_fields = ["created_at", "updated_at", "total_cost"]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "Замовлення повинно містити хоча б одну книгу."
            )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            book = item_data["book"]
            quantity = item_data["quantity"]
            OrderItem.objects.create(
                order=order,
                book=book,
                price=book.price,
                quantity=quantity,
            )
        return order


# --- СЕРІАЛІЗАТОРИ ДЛЯ СЕСІЙНОГО КОШИКА (my_app.cart.Cart) ---


class CartItemSerializer(serializers.Serializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        write_only=True,
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    override_quantity = serializers.BooleanField(default=False, write_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )


class CartSerializer(serializers.Serializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
