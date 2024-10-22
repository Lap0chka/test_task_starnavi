from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import Post, Comment
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken


class PostViewSetTest(APITestCase):
    def setUp(self) -> None:
        """
        Set up test data including users, posts, and URLs.
        """
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass',
                                                        email='admin@example.com')
        self.user = User.objects.create_user(username='user', password='userpass', email='user@example.com')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass',
                                                   email='other@example.com')

        self.post = Post.objects.create(title="Test Post", slug="test-post", author=self.user,
                                        body="Content of the test post.", status="PB")
        self.url_list = reverse('post-list')
        self.url_detail = reverse('post-detail', kwargs={'slug': self.post.slug})

        self.valid_payload = {"title": "Updated Post", "body": "Updated content"}
        self.invalid_payload = {"title": "", "body": "Content"}

        self.url_range = self.url_detail + 'comments-range/2024-01-01/2024-12-31/'

        self.comment1 = Comment.objects.create(
            post=self.post,
            author=self.user,
            body="First comment",
            created=datetime(2024, 6, 1)
        )
        self.comment2 = Comment.objects.create(
            post=self.post,
            author=self.user,
            body="Second comment",
            created=datetime(2024, 8, 15)
        )
        self.comment_outside_range = Comment.objects.create(
            post=self.post,
            author=self.user,
            body="Out of range comment",
        )

        self.comment_outside_range.created = datetime(2022, 12, 31)
        self.comment_outside_range.save()

    def get_jwt_token(self, user: User) -> str:
        """
        Helper method to generate a JWT token for a user.
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)  # type: ignore[attr-defined]

    def test_create_post(self) -> None:
        """
        Test that an authenticated and staff user with a JWT token can create a post.
        """
        for num, user in enumerate([self.user, self.admin_user]):
            token = self.get_jwt_token(user)
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

            response: Response = self.client.post(self.url_list, {
                "title": f"New Post{num}",
                "slug": f"new-post{num}",
                "body": "Content for the new post"
            })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(Post.objects.filter(slug=f"new-post{num}").exists())

    def test_create_post_unauthorized_user(self) -> None:
        """
        Test that an authenticated and staff user with a JWT token can create a post.
        """

        response: Response = self.client.post(self.url_list, {
            "title": "New Post",
            "slug": "new-post",
            "body": "Content for the new post"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_post_with_comments(self) -> None:
        """
        Test retrieving a post along with its comments.
        """
        Comment.objects.create(post=self.post, author=self.user, body="First comment")
        Comment.objects.create(post=self.post, author=self.other_user, body="Second comment")

        response: Response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('post', response.data)
        self.assertIn('comments', response.data)
        self.assertEqual(len(response.data['comments']), 5)

    def test_update_post_by_author_and_admin(self) -> None:
        """
        Test that the post author can update their post.
        """
        for user in [self.user, self.admin_user]:
            token = self.get_jwt_token(user)
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            response: Response = self.client.patch(self.url_detail, self.valid_payload)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.post.refresh_from_db()
            self.assertEqual(self.post.title, "Updated Post")

    def test_update_post_by_non_author(self) -> None:
        """
        Test that a non-author user cannot update another user's post.
        """
        token = self.get_jwt_token(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response: Response = self.client.patch(self.url_detail, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_by_admin_and_user(self) -> None:
        """
        Test that an admin  can delete any post.
        """
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response: Response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(slug="test-post").exists())

    def test_delete_post_by_non_author(self) -> None:
        """
        Test that a non-author user cannot delete another user's post.
        """
        token = self.get_jwt_token(self.other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response: Response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_comments_in_date_range_success(self) -> None:
        """
        Test that comments within the specified date range are returned successfully.
        """
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response: Response = self.client.get(self.url_range)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('comments', response.data)
        self.assertEqual(len(response.data['comments']), 2)
        self.assertNotIn('Out of range comment', [comment['body'] for comment in response.data['comments']])

    def test_comments_in_date_range_no_comments(self) -> None:
        """
        Test that an empty list is returned when no comments fall within the date range.
        """
        # Используем диапазон, где нет комментариев
        self.url = self.url_detail + 'comments-range/2025-01-01/2025-12-31/'
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response: Response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('comments', response.data)
        self.assertEqual(len(response.data['comments']), 0)
