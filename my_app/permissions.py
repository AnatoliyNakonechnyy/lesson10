# my_app/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Дозволяє редагувати або видаляти об'єкт лише його власнику (user).
    Іншим користувачам доступне лише читання (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user", None) == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Повний доступ має лише власник об'єкта (user) або адміністратор (is_staff).
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return getattr(obj, "user", None) == request.user
