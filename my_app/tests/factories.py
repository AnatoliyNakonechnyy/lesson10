import factory
from django.contrib.auth import get_user_model
from my_app.models import Book

try:
    from my_app.models import Category
except ImportError:
    Category = None

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    phone_number = "+380991112233"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Виправлено: Передаємо правильну кількість аргументів у сучасний _get_manager."""
        password = kwargs.pop("password", "SecurePass123!QAZ")
        manager = cls._get_manager(model_class)  # <-- ВИПРАВЛЕНО ТУТ
        return manager.create_user(*args, password=password, **kwargs)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category if Category else object

    name = factory.Sequence(lambda n: f"Category {n}")


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f"Book Title {n}")
    author = factory.Faker("name")
    price = 29.99
    stock = 15
    category = factory.SubFactory(CategoryFactory) if Category else None
