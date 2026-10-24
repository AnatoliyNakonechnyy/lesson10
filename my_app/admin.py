from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Book, Category, CustomUser, Order, OrderItem


class BookInline(admin.TabularInline):
    model = Book
    extra = 1
    fields = (
        "title",
        "author",
        "price",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines: ClassVar[list] = [BookInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price")
    list_display_links = ("title",)
    search_fields = ("title", "description")
    list_editable = ("price",)
    list_filter = ("category",)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "phone_number", "is_staff", "is_active")

    fieldsets: ClassVar[tuple] = UserAdmin.fieldsets + (
        ("Additional Information", {"fields": ("phone_number", "bio")}),
    )
    add_fieldsets: ClassVar[tuple] = UserAdmin.add_fieldsets + (
        ("Additional Information", {"fields": ("phone_number", "bio")}),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields: ClassVar[list] = ["book"]
    extra = 0
    fields = ("book", "price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "status",
        "created_at",
    )
    list_display_links = ("id",)
    list_filter = ("status", "created_at")
    search_fields = ("id", "first_name", "last_name", "email")
    inlines: ClassVar[list] = [OrderItemInline]
    readonly_fields: ClassVar[list] = ["created_at", "updated_at"]

    fieldsets: ClassVar[tuple] = (
        ("Order Information", {"fields": ("status", "user")}),
        (
            "Customer Details",
            {"fields": ("first_name", "last_name", "email", "phone")},
        ),
        ("Shipping Address", {"fields": ("city", "address")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
