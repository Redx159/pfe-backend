from rest_framework.permissions import BasePermission


class CanManageMeetings(BasePermission):
    """
    Only ADMIN / HR / MANAGER
    """

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in ("ADMIN", "HR", "MANAGER")
        )
