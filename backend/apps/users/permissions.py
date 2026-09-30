from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.role == "ADMIN" or user.is_superuser))


class IsAdminOrReadCreateStaff(permissions.BasePermission):
    """Admins have full access. Staff may read and perform operational writes."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == "ADMIN" or user.is_superuser:
            return True
        if user.role == "STAFF":
            return request.method in ("GET", "HEAD", "OPTIONS", "POST", "PATCH")
        return False
