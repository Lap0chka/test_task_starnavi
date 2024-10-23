from datetime import timedelta
from typing import Any

from better_profanity import profanity
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .tasks import set_auto_response_parent

User = get_user_model()


def check_swearing(text: str) -> bool:
    """
    Checks if the given text contains any profanity.
    """
    return bool(profanity.contains_profanity(text))


class PublishedManager(models.Manager):
    """
    Custom manager for retrieving only published posts.
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Override the default queryset to filter published posts.

        """
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """
    Model representing a blog post.
    """

    class Status(models.TextChoices):
        """
        Enum for post status.
        """

        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blog_posts", null=True, blank=True
    )
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT
    )
    auto_response_comment = models.TextField(default="", blank=True)
    time_response = models.IntegerField(default=0)
    amount_block_comment = models.PositiveIntegerField(default=0)
    objects = models.Manager()
    published = PublishedManager()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Checks if the title or body of the post contains any profane words before saving.
        """
        if check_swearing(self.title) or check_swearing(self.body):
            raise ValidationError("You cannot use swearing words in the title or body.")

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the post.
        """
        return f"{self.title}"


class Comment(models.Model):
    """
    Model representing a comment on a post.
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Saves the comment instance after performing custom validation and modifications.
        If the post has an `auto_response_comment` and the comment doesn't have a parent,
        sets the parent to the post's auto-response comment.
        """
        if check_swearing(self.body):
            self.post.amount_block_comment += 1
            self.post.save(update_fields=["amount_block_comment"])
            raise ValidationError("You cannot use swearing words in the title or body.")

        super().save(*args, **kwargs)

        if self.post.auto_response_comment and not self.parent:
            time_response_minutes = self.post.time_response
            set_auto_response_parent.apply_async(
                (self.id,),
                eta=timezone.now() + timedelta(minutes=time_response_minutes),
            )

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the comment.
        """
        return f"Comment by {self.author} on {self.post}"
