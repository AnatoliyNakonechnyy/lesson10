from importlib import import_module, util

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("my_app.urls", namespace="store")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if util.find_spec("debug_toolbar") is not None:
        debug_toolbar = import_module("debug_toolbar")
        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
