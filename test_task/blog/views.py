from typing import Any, Optional

from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from .models import Comment, Post
from .permissions import IsAdminOrMyNoteOrReadOnly
from .serializers import CommentSerializer, PostSerializer


class ResultsSetPagination(PageNumberPagination):
    """Custom pagination class to control the pagination of results."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts.

    Admin users can update or delete any post.
    Regular users can update or delete only their own posts.
    """

    queryset = Post.published.all()
    serializer_class = PostSerializer
    pagination_class = ResultsSetPagination
    permission_classes = [IsAdminOrMyNoteOrReadOnly]
    lookup_field = "slug"

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Automatically set the author field to the current user when creating a comment.
        """
        serializer.save(author=self.request.user)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieve a post and its comments."""
        post = get_object_or_404(Post, slug=self.kwargs[self.lookup_field])
        comments = Comment.objects.filter(post=post)
        post_serializer = PostSerializer(post)
        comments_serializer = CommentSerializer(comments, many=True)
        return Response(
            {"post": post_serializer.data, "comments": comments_serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path=r"comments-range/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})",
    )
    def comments_in_date_range(
        self,
        request: Request,
        slug: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Response:
        """
        Retrieve comments for a specific post within a specified date range.
        """
        if not request.user.is_staff:
            raise PermissionDenied(
                "Unfortunately you dont have permission to perform this action."
            )
        post = get_object_or_404(Post, slug=slug)

        date_from = parse_date(date_from)
        date_to = parse_date(date_to)

        if not date_from or not date_to:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        comments = Comment.objects.filter(
            post=post, created__date__gte=date_from, created__date__lte=date_to
        )

        serializer = CommentSerializer(comments, many=True)
        comments_count = comments.count()
        amount_block_comment = post.amount_block_comment
        response_data = {
            "comments": serializer.data,
            "comments_create": comments_count,
            "block_comment": amount_block_comment,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing comments."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = ResultsSetPagination
    permission_classes = [IsAdminOrMyNoteOrReadOnly]
    lookup_field = "slug"

    def perform_create(self, serializer: BaseSerializer) -> None:
        """
        Automatically set the author field to the current user when creating a comment.
        """
        serializer.save(author=self.request.user)
