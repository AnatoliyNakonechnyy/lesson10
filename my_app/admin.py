from django.contrib import admin

from .models import Book, Category


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "price")

    list_display_links = ("title",)

    search_fields = ("title", "description")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")

    list_display_links = ("name",)

    search_fields = ("name",)
