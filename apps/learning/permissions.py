from rest_framework import permissions


class IsInstructorOrReadOnly(permissions.BasePermission):
    """Anyone authenticated can read; only instructors can create/edit/delete."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_instructor)
