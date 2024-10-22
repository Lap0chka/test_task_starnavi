from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsNotAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow access to unauthenticated users.
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """
        Return True if the user is not authenticated, otherwise False.
        """
        return not request.user.is_authenticated
