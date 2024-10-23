from typing import Any, Dict

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates that the passwords match and that the email is unique.
    """

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Password for the user.",
    )
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Confirmation password.",
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2")

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that both password fields match and that the email is not already registered.
        """
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("The passwords do not match.")
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Email already registered.")
        return data

    def create(self, validated_data: Dict[str, Any]) -> Any:
        """
        Create a new user with the validated data.
        """
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user
