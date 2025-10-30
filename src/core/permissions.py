from rest_framework import permissions


class IsAdminUserRole(permissions.BasePermission):
    """
    Custom permission to only allow users with 'admin' role to access the API.
    This checks the custom User model's role field.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has admin role
        # Since we're using AUTH_USER_MODEL, request.user is our custom User model
        return hasattr(request.user, 'role') and request.user.role == 'admin'


