from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Name of the book"))
    author = models.CharField(max_length=255, verbose_name=_("Author"))
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Price")
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="books",
        verbose_name=_("Category"),
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")
        indexes = [models.Index(fields=["category"], name="book_category_idx")]
