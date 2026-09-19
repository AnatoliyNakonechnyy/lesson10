from django.db import models


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
