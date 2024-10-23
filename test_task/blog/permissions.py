from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsAdminOrMyNoteOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow access to admins for all posts,
    and to allow users to access only their own posts.
    """

    def has_permission(self, request: Request, view: View) -> bool:
        """
         Allow access to list and retrieve actions for everyone,
        but require authentication for other actions.
        """
        if view.action in ["list", "retrieve"]:
            return True

        return bool(request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Allow access if the user is an admin or if the user is the owner of the object.
        """
        if request.user.is_staff:
            return True

        return bool(obj.author == request.user)
