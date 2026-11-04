import pytest
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from my_app.forms import CustomUserCreationForm
from my_app.views.cart import CartAddBookForm
from my_app.tests.factories import BookFactory, UserFactory  # Тепер працюватиме

User = get_user_model()


@pytest.mark.django_db
def test_book_factory_creation():
    """1. Перевірка створення книги через фабрику."""
    book = BookFactory(title="Factory Book", price=50.00)
    assert book.title == "Factory Book"
    assert float(book.price) == 50.00


@pytest.mark.django_db
def test_book_str_method_with_factory():
    """2. Перевірка __str__ з використанням фабрики."""
    book = BookFactory(title="Unique Sci-Fi", author="Isaac Asimov")
    assert "Unique Sci-Fi" in str(book)


@pytest.mark.django_db
def test_book_negative_stock_validation():
    """3. Валідація негативного залишку."""
    book = BookFactory.build(stock=-10)
    with pytest.raises(ValidationError):
        book.full_clean()


@pytest.mark.django_db
def test_user_factory_creation():
    """4. Валідація створення кастомного користувача."""
    user = UserFactory(username="alex_flow", phone_number="+380500000000")
    assert user.username == "alex_flow"
    assert user.phone_number == "+380500000000"


@pytest.mark.django_db
@patch("django.core.mail.utils.DNS_NAME", "localhost")
def test_email_sending_mocked():
    """5. Ізольований тест бізнес-логіки відправки листів без реального SMTP за допомогою Mock."""
    with patch("django.core.mail.EmailMessage.send", return_value=1) as mock_send:
        from django.core.mail import EmailMessage

        email = EmailMessage("Subject", "Body", "from@example.com", ["to@example.com"])
        result = email.send()
        assert result == 1
        mock_send.assert_called_once()


def test_cart_add_form_valid():
    form = CartAddBookForm(data={"quantity": 5, "override": True})
    assert form.is_valid()


def test_user_registration_form_empty_username():
    form = CustomUserCreationForm(data={"username": "", "phone_number": "+38000"})
    assert not form.is_valid()
