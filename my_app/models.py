from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Name of the book")

    author = models.CharField(max_length=255, verbose_name="Author")

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")

    description = models.TextField(blank=True, verbose_name="Description")

    stock = models.PositiveIntegerField(default=0, verbose_name="Stock")

    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name="Category",
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name of the category")
    slug = models.SlugField(
        max_length=255, unique=True, verbose_name="Slug of the category"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
