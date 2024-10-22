from typing import Any
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from .permissions import IsNotAuthenticated
from .serializers import UserRegisterSerializer

User = get_user_model()


class UserCreateView(generics.CreateAPIView):
    """
    API view for creating a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [IsNotAuthenticated]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handles POST requests to create a new user.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
