import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from my_app.tests.factories import BookFactory, UserFactory

User = get_user_model()


@pytest.fixture
def auth_client(client):
    user = UserFactory(username="customer_flow")
    client.login(username="customer_flow", password="SecurePass123!QAZ")
    return client, user


# ==========================================
# INTEGRATION: АСИНХРОННИЙ КАТАЛОГ ТА ПОШУК
# ==========================================


@pytest.mark.django_db
def test_async_book_list_with_factories(client):
    BookFactory(title="Python Microservices")
    response = client.get("/en/books/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_async_book_list_search_with_factories(client):
    BookFactory(title="Django Pro")
    response = client.get("/en/books/?q=Django")
    assert response.status_code == 200


@pytest.mark.django_db
def test_async_book_detail_flow(client):
    book = BookFactory()
    response = client.get(f"/en/books/{book.pk}/")
    assert response.status_code == 200


# ==========================================
# INTEGRATION: ФЛОУ КОРЗИНИ ТА ЗАМОВЛЕНЬ
# ==========================================


@pytest.mark.django_db
def test_cart_add_integration_flow(client):
    book = BookFactory()
    response = client.post(
        f"/en/cart/add/{book.pk}/", {"quantity": 2, "override": False}
    )
    assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_empty_cart_page(client):
    response = client.get("/en/cart/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_language_switch_flow(client):
    assert client.get("/uk/").status_code == 200
    assert client.get("/en/").status_code == 200
