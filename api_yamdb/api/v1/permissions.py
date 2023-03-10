from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission to only allow admin users to perform unsafe methods."""

    def has_permission(self, request, view):
        """Whether the user has permission to perform the request."""
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAuthor(permissions.BasePermission):
    """Permission to allow author-only access to the object."""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
            and request.method in ['patch', 'retrieve']
        )


class IsAdmin(permissions.BasePermission):
    """Role-based administrator permission class."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class AuthorOrStaffOrReadOnly(permissions.BasePermission):
    """Base permission for common user functionality.
    Allows safe methods for all users, unsafe only for authors and staff."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            view.action == 'retrieve'
            or obj.author == request.user
            or request.user.is_admin
            or (request.user.is_moderator
                and view.action != 'post')
        )
