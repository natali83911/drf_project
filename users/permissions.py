from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerOrModerator(BasePermission):
    """Разрешение для владельца или модератора."""
    def has_object_permission(self, request, view, obj):
        is_owner = obj.owner == request.user
        is_moderator = request.user.groups.filter(name='moderators').exists()
        return is_owner or is_moderator