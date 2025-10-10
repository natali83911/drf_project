from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrModeratorCanEditReadNoCreateDelete(BasePermission):
    """
    Модераторы могут читать и редактировать любые объекты,
    но НЕ создавать и НЕ удалять.
    Владельцы могут читать, редактировать и удалять свои объекты.
    """

    def has_permission(self, request, view):
        user = request.user
        is_moderator = user.groups.filter(name="moderators").exists()

        if not user.is_authenticated:
            return False

        # Модераторы запрещено создавать и удалять
        if is_moderator and request.method in ["POST", "DELETE"]:
            return False

        return True  # остальные запросы всем аутентифицированным открыты

    def has_object_permission(self, request, view, obj):
        user = request.user
        is_moderator = user.groups.filter(name="moderators").exists()

        # Модераторы могут читать и редактировать, но не создавать и удалять (уже проверено в has_permission)
        if is_moderator:
            if request.method in permissions.SAFE_METHODS or request.method in [
                "PUT",
                "PATCH",
            ]:
                return True
            else:
                return False

        # Владельцы могут всё со своими объектами
        return obj.owner == user
