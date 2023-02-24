from rest_framework import permissions


# для управления аккаунтом
class IsAuthor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
            and request.method in ['patch', 'retrieve']
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


# для просмотра и создания объектов title, comments
class AuthorOrStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            view.action == 'retrieve'
            or obj.author == request.user
            or request.user.is_admin
            or (request.user.is_moderator
                and view.action != 'post')
        )
