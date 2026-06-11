from rest_framework.permissions import BasePermission

class IsAdminUserRole(BasePermission):
    """
    Custom Permission class untuk Django REST Framework (DRF).
    Hanya mengizinkan akses ke user yang terautentikasi dan memiliki role 'admin'.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )
