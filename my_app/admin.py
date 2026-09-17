from typing import ClassVar

from django.contrib import admin

from .models import Book, Category


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
