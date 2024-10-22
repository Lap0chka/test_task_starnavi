from celery import shared_task
from typing import Any, Optional
from django.apps import apps


@shared_task
def set_auto_response_parent(comment_id: int) -> None:
    """
    Sets the parent of a comment to the post's auto-response comment after a delay.

    This function is used to automatically set the `parent` field of a comment
    to `post.auto_response_comment` if the comment was created without a parent,
    and if the post has an `auto_response_comment`. This is executed after a delay
    specified by the `time_response` attribute of the post.
    """
    try:
        Comment: Any = apps.get_model('blog', 'Comment')
        comment: Optional[Any] = Comment.objects.get(id=comment_id)

        if comment is None:
            raise RuntimeError('Comment not found')

        Comment.objects.create(
            post=comment.post,
            body=comment.post.auto_response_comment,
            author=comment.post.author,
        )
    except Exception:
        raise RuntimeError('Something went wrong, try again')
