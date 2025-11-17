from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Allow only admins full access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role.lower() == 'admin')


class IsUser(BasePermission):
    """
    Allow only regular users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and not (request.user.is_superuser or request.user.role.lower() == 'admin')


class IsAdminOrReadOnly(BasePermission):
    """
    Admins can GET, POST, PUT, DELETE.
    Users/anonymous can only GET.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role.lower() == 'admin')


class IsOwnerOrAdmin(BasePermission):
    """
    For objects related to a user (applications),
    users can only access their own.
    Admin can access all.
    """
    def has_object_permission(self, request, view, obj):
        if (request.user.is_superuser or request.user.role.lower() == 'admin'):
            return True
        return obj.user == request.user
