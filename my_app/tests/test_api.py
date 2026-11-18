# my_app/test_api.py
from decimal import Decimal
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from my_app.models import Category, Book, Order


User = get_user_model()

TEST_CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}


@override_settings(CACHES=TEST_CACHES)
class BookstoreAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

        # Тестові користувачі
        self.admin = User.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="StrongPassword123!",
        )
        self.user1 = User.objects.create_user(
            username="reader1",
            email="reader1@example.com",
            password="StrongPassword123!",
        )
        self.user2 = User.objects.create_user(
            username="reader2",
            email="reader2@example.com",
            password="StrongPassword123!",
        )

        # Категорії та книги
        self.cat_fiction = Category.objects.create(name="Fiction", slug="fiction")
        self.cat_science = Category.objects.create(name="Science", slug="science")

        self.book1 = Book.objects.create(
            title="Dune",
            author="Frank Herbert",
            price=Decimal("25.00"),
            description="Epic sci-fi novel",
            stock=10,
            category=self.cat_fiction,
        )
        self.book2 = Book.objects.create(
            title="A Brief History of Time",
            author="Stephen Hawking",
            price=Decimal("18.50"),
            description="Cosmology for everyone",
            stock=5,
            category=self.cat_science,
        )

    # --- 1. JWT АВТОРИЗАЦІЯ (3 тести) ---

    def test_01_jwt_obtain_token(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "reader1", "password": "StrongPassword123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_02_jwt_refresh_token(self):
        login = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "reader1", "password": "StrongPassword123!"},
        )
        response = self.client.post(
            reverse("token_refresh"),
            {"refresh": login.data["refresh"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_03_jwt_verify_token(self):
        login = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "reader1", "password": "StrongPassword123!"},
        )
        response = self.client.post(
            reverse("token_verify"),
            {"token": login.data["access"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- 2. CATEGORIES (2 тести) ---

    def test_04_get_categories_public(self):
        response = self.client.get(reverse("api-category-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_05_create_category_permissions(self):
        # Звичайний користувач отримує 403
        self.client.force_authenticate(user=self.user1)
        res_user = self.client.post(
            reverse("api-category-list"),
            {"name": "History", "slug": "history"},
        )
        self.assertEqual(res_user.status_code, status.HTTP_403_FORBIDDEN)

        # Адміністратор створює успішно
        self.client.force_authenticate(user=self.admin)
        res_admin = self.client.post(
            reverse("api-category-list"),
            {"name": "History", "slug": "history"},
        )
        self.assertEqual(res_admin.status_code, status.HTTP_201_CREATED)

    # --- 3. BOOKS, ФІЛЬТРАЦІЯ ТА ПАГІНАЦІЯ (4 тести) ---

    def test_06_get_books_with_nested_category(self):
        response = self.client.get(reverse("api-book-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("name", response.data["results"][0]["category"])

    def test_07_create_book_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "title": "1984",
            "author": "George Orwell",
            "price": "15.00",
            "description": "Dystopian novel",
            "stock": 20,
            "category_id": self.cat_fiction.id,
        }
        response = self.client.post(reverse("api-book-list"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category"]["id"], self.cat_fiction.id)

    def test_08_filter_books_by_category_and_price(self):
        response = self.client.get(
            reverse("api-book-list"),
            {"category": self.cat_fiction.id, "price__gte": "20.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Dune")

    def test_09_books_pagination_20_items_per_page(self):
        extra_books = [
            Book(
                title=f"Test Book {i}",
                author="Test Author",
                price=Decimal("10.00"),
                stock=5,
                category=self.cat_fiction,
            )
            for i in range(23)
        ]
        Book.objects.bulk_create(extra_books)

        response = self.client.get(reverse("api-book-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 20)
        self.assertIsNotNone(response.data["next"])

    # --- 4. CART (2 тести) ---

    def test_10_add_item_to_cart(self):
        response = self.client.post(
            reverse("api-cart-add-item"),
            {"book_id": self.book1.id, "quantity": 2},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 2)
        self.assertEqual(Decimal(response.data["total_price"]), Decimal("50.00"))

    def test_11_clear_cart(self):
        self.client.post(
            reverse("api-cart-add-item"),
            {"book_id": self.book1.id, "quantity": 1},
        )
        response = self.client.post(reverse("api-cart-clear-cart"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 0)

    # --- 5. ORDERS ТА ПРАВА ДОСТУПУ (2 тести) ---

    def test_12_create_order_authenticated_with_nested_items(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            "first_name": "Taras",
            "last_name": "Shevchenko",
            "email": "taras@example.com",
            "phone": "+380991112233",
            "address": "Khreshchatyk 1",
            "city": "Kyiv",
            "items": [
                {"book_id": self.book1.id, "quantity": 2},
                {"book_id": self.book2.id, "quantity": 1},
            ],
        }
        response = self.client.post(reverse("api-order-list"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data["total_cost"]), Decimal("68.50"))
        self.assertEqual(len(response.data["items"]), 2)

    def test_13_user_cannot_access_other_user_order(self):
        other_order = Order.objects.create(
            user=self.user2,
            first_name="U2",
            last_name="Test",
            email="u2@test.com",
            phone="456",
            address="Addr 2",
            city="Odesa",
        )
        self.client.force_authenticate(user=self.user1)
        url = reverse("api-order-detail", args=[other_order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- 6. SWAGGER DOCS ТА CORS (2 тести) ---

    def test_14_swagger_docs_accessible(self):
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_15_cors_headers_on_api_response(self):
        response = self.client.get(
            reverse("api-book-list"),
            HTTP_ORIGIN="http://localhost:3000",
        )
        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"),
            "http://localhost:3000",
        )
