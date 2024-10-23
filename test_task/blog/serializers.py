from typing import Union

from rest_framework import serializers

from .models import Comment, Post


class PostSerializer(serializers.ModelSerializer):
    """Serializer for the Book model."""

    class Meta:
        model = Post
        fields: Union[list[str], str] = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the Comment model."""

    class Meta:
        model = Comment
        fields: Union[list[str], str] = "__all__"
