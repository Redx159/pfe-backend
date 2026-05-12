from rest_framework.permissions import BasePermission


class IsHRAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and hasattr(user, "role")
            and user.role in ["ADMIN", "HR", "MANAGER"]
        )
