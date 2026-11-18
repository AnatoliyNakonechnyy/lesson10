from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from my_app.api_views import (
    CategoryViewSet,
    BookViewSet,
    OrderViewSet,
    CartViewSet,
)

# Налаштування роутера для ViewSets
router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="api-category")
router.register(r"books", BookViewSet, basename="api-book")
router.register(r"orders", OrderViewSet, basename="api-order")
router.register(r"cart", CartViewSet, basename="api-cart")

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    # REST API маршрути (без мовного префікса)
    path("api/", include(router.urls)),
    # JWT авторизація
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # OpenAPI схема та Swagger документація на /api/docs/
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

# Веб-маршрути сайту з підтримкою мовних префіксів (/uk/, /en/)
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("my_app.urls", namespace="store")),
)
