from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Comment, Follow, Like, Post


User = get_user_model()


class SideQuestAPITests(APITestCase):
    def setUp(self):
        self.standard_group = Group.objects.create(name="standard_users")
        self.moderator_group = Group.objects.create(name="moderators")

        self.user = self.create_user("user_demo", "user12345")
        self.alice = self.create_user("alice_demo", "alice12345")
        self.bob = self.create_user("bob_demo", "bob12345")
        self.moderator = self.create_user("moderator_demo", "moderator12345")
        self.moderator.groups.add(self.moderator_group)

        self.user_post = Post.objects.create(
            author=self.user,
            content="My first side quest survives contact with reality.",
        )
        self.alice_post = Post.objects.create(
            author=self.alice,
            content="A tiny raven now guards my notebook.",
        )
        self.bob_post = Post.objects.create(
            author=self.bob,
            content="The miniature is 80 percent primer and 20 percent hope.",
        )

    def create_user(self, username, password):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=password,
        )
        user.groups.add(self.standard_group)
        return user

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_valid_registration_returns_201(self):
        response = self.client.post(
            "/api/v1/auth/register/",
            {
                "username": "new_user",
                "email": "new_user@example.com",
                "bio": "New quester.",
                "password": "StrongPass12345!",
                "password_confirm": "StrongPass12345!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_incorrect_jwt_login_is_rejected(self):
        response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": self.user.username,
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correct_jwt_login_returns_tokens(self):
        response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": self.user.username,
                "password": "user12345",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_auth_me_requires_authentication(self):
        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_auth_me_returns_current_user(self):
        self.authenticate(self.user)

        response = self.client.get("/api/v1/auth/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["username"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)

    def test_public_user_list_does_not_expose_email(self):
        response = self.client.get("/api/v1/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("email", response.data[0])

    def test_public_profile_detail_includes_statistics(self):
        Post.objects.create(
            author=self.user,
            content="Another quest log entry.",
        )
        Follow.objects.create(follower=self.alice, followed=self.user)
        Follow.objects.create(follower=self.user, followed=self.bob)

        response = self.client.get(f"/api/v1/users/{self.user.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["posts_count"], 2)
        self.assertEqual(response.data["followers_count"], 1)
        self.assertEqual(response.data["following_count"], 1)
        self.assertNotIn("email", response.data)

    def test_public_user_list_includes_statistics(self):
        Follow.objects.create(follower=self.alice, followed=self.user)

        response = self.client.get("/api/v1/users/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        first_user = response.data[0]
        self.assertIn("posts_count", first_user)
        self.assertIn("followers_count", first_user)
        self.assertIn("following_count", first_user)
        self.assertNotIn("email", first_user)

    def test_anonymous_post_creation_returns_401(self):
        response = self.client.post(
            "/api/v1/posts/",
            {"content": "Anonymous quest."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_post_creation_returns_201(self):
        self.authenticate(self.user)

        response = self.client.post(
            "/api/v1/posts/",
            {"content": "Today I debugged the shelf."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author_username"], self.user.username)
        self.assertEqual(response.data["likes_count"], 0)
        self.assertEqual(response.data["comments_count"], 0)

    def test_post_response_includes_readability_fields(self):
        Like.objects.create(user=self.alice, post=self.user_post)
        Comment.objects.create(
            author=self.alice,
            post=self.user_post,
            content="Readable response confirmed.",
        )

        response = self.client.get(f"/api/v1/posts/{self.user_post.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["author_username"], self.user.username)
        self.assertEqual(response.data["likes_count"], 1)
        self.assertEqual(response.data["comments_count"], 1)

    def test_owner_can_patch_own_post(self):
        self.authenticate(self.user)

        response = self.client.patch(
            f"/api/v1/posts/{self.user_post.id}/",
            {"content": "Updated quest log."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_post.refresh_from_db()
        self.assertEqual(self.user_post.content, "Updated quest log.")

    def test_non_owner_cannot_patch_another_users_post(self):
        self.authenticate(self.bob)

        response = self.client.patch(
            f"/api/v1/posts/{self.user_post.id}/",
            {"content": "Claimed quest."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_own_post(self):
        self.authenticate(self.user)

        response = self.client.delete(f"/api/v1/posts/{self.user_post.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.user_post.id).exists())

    def test_comment_creation_works_for_authenticated_user(self):
        self.authenticate(self.user)

        response = self.client.post(
            f"/api/v1/posts/{self.alice_post.id}/comments/",
            {"content": "This raven has excellent posture."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author_username"], self.user.username)

    def test_comment_response_includes_author_username(self):
        comment = Comment.objects.create(
            author=self.alice,
            post=self.user_post,
            content="Readable comment.",
        )

        response = self.client.get(f"/api/v1/posts/{self.user_post.id}/comments/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment_data = next(item for item in response.data if item["id"] == comment.id)
        self.assertEqual(comment_data["author_username"], self.alice.username)

    def test_non_owner_cannot_edit_another_users_comment(self):
        comment = Comment.objects.create(
            author=self.alice,
            post=self.user_post,
            content="Original comment.",
        )
        self.authenticate(self.bob)

        response = self.client.patch(
            f"/api/v1/comments/{comment.id}/",
            {"content": "Edited comment."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_self_follow_returns_400(self):
        self.authenticate(self.user)

        response = self.client.post(f"/api/v1/users/{self.user.id}/follow/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_follow_returns_400(self):
        Follow.objects.create(follower=self.user, followed=self.alice)
        self.authenticate(self.user)

        response = self.client.post(f"/api/v1/users/{self.alice.id}/follow/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_like_returns_400(self):
        Like.objects.create(user=self.user, post=self.alice_post)
        self.authenticate(self.user)

        response = self.client.post(f"/api/v1/posts/{self.alice_post.id}/like/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_feed_includes_current_and_followed_posts(self):
        Follow.objects.create(follower=self.user, followed=self.alice)
        self.authenticate(self.user)

        response = self.client.get("/api/v1/feed/")

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user_post.id, post_ids)
        self.assertIn(self.alice_post.id, post_ids)

    def test_feed_excludes_unfollowed_user_posts(self):
        Follow.objects.create(follower=self.user, followed=self.alice)
        self.authenticate(self.user)

        response = self.client.get("/api/v1/feed/")

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.bob_post.id, post_ids)

    def test_user_posts_returns_only_selected_users_posts(self):
        Post.objects.create(
            author=self.user,
            content="Another selected user post.",
        )

        response = self.client.get(f"/api/v1/users/{self.user.id}/posts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post_ids = {item["id"] for item in response.data["results"]}
        self.assertIn(self.user_post.id, post_ids)
        self.assertNotIn(self.alice_post.id, post_ids)
        self.assertNotIn(self.bob_post.id, post_ids)

    def test_user_posts_missing_user_returns_404(self):
        response = self.client.get("/api/v1/users/999999/posts/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_list_pagination_returns_expected_shape(self):
        response = self.client.get("/api/v1/posts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_post_list_with_html_accept_returns_json_200(self):
        response = self.client.get(
            "/api/v1/posts/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.accepted_renderer.format, "json")
        self.assertIn("application/json", response["Content-Type"])
        self.assertIn("results", response.data)

    def test_post_list_with_json_accept_returns_json_200(self):
        response = self.client.get(
            "/api/v1/posts/",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.accepted_renderer.format, "json")
        self.assertIn("application/json", response["Content-Type"])
        self.assertIn("results", response.data)

    def test_post_list_page_size_works(self):
        for index in range(5):
            Post.objects.create(
                author=self.user,
                content=f"Page size quest {index}.",
            )

        response = self.client.get("/api/v1/posts/?page_size=2")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_post_list_page_size_cannot_exceed_maximum(self):
        for index in range(60):
            Post.objects.create(
                author=self.user,
                content=f"Maximum page quest {index}.",
            )

        response = self.client.get("/api/v1/posts/?page_size=99")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 50)

    def test_post_search_matches_content(self):
        guitar_post = Post.objects.create(
            author=self.user,
            content="Practiced guitar until the chord sounded honest.",
        )

        response = self.client.get("/api/v1/posts/?search=guitar")

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(guitar_post.id, post_ids)
        self.assertNotIn(self.alice_post.id, post_ids)

    def test_post_search_matches_author_username(self):
        response = self.client.get("/api/v1/posts/?search=alice")

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.alice_post.id, post_ids)
        self.assertNotIn(self.user_post.id, post_ids)

    def test_post_author_filter_works(self):
        response = self.client.get(f"/api/v1/posts/?author={self.alice.id}")

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.alice_post.id, post_ids)
        self.assertNotIn(self.user_post.id, post_ids)

    def test_post_created_after_filter_works(self):
        old_post = Post.objects.create(
            author=self.user,
            content="Old quest.",
        )
        Post.objects.filter(id=old_post.id).update(
            created_at=timezone.make_aware(datetime(2026, 5, 1))
        )

        response = self.client.get("/api/v1/posts/?created_after=2026-06-01")

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(old_post.id, post_ids)

    def test_post_created_before_filter_works(self):
        old_post = Post.objects.create(
            author=self.user,
            content="Older quest.",
        )
        Post.objects.filter(id=old_post.id).update(
            created_at=timezone.make_aware(datetime(2026, 5, 1))
        )

        response = self.client.get("/api/v1/posts/?created_before=2026-06-01")

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(old_post.id, post_ids)
        self.assertNotIn(self.user_post.id, post_ids)

    def test_user_posts_endpoint_is_paginated(self):
        for index in range(12):
            Post.objects.create(
                author=self.user,
                content=f"User post page quest {index}.",
            )

        response = self.client.get(f"/api/v1/users/{self.user.id}/posts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 13)
        self.assertEqual(len(response.data["results"]), 10)

    def test_user_posts_search_stays_within_selected_user(self):
        user_post = Post.objects.create(
            author=self.user,
            content="Guitar practice notes.",
        )
        alice_post = Post.objects.create(
            author=self.alice,
            content="Guitar strings and ravens.",
        )

        response = self.client.get(
            f"/api/v1/users/{self.user.id}/posts/?search=guitar"
        )

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(user_post.id, post_ids)
        self.assertNotIn(alice_post.id, post_ids)

    def test_user_posts_author_filter_cannot_escape_selected_user_scope(self):
        response = self.client.get(
            f"/api/v1/users/{self.user.id}/posts/?author={self.alice.id}"
        )

        post_ids = {item["id"] for item in response.data["results"]}
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post_ids, set())

    def test_feed_pagination_works(self):
        Follow.objects.create(follower=self.user, followed=self.alice)
        self.authenticate(self.user)

        response = self.client.get("/api/v1/feed/?page_size=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertEqual(len(response.data["results"]), 1)

    def test_normal_user_cannot_block_accounts(self):
        self.authenticate(self.user)

        response = self.client.post(
            f"/api/v1/moderation/users/{self.bob.id}/block/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_block_and_unblock_another_user(self):
        self.authenticate(self.moderator)

        block_response = self.client.post(
            f"/api/v1/moderation/users/{self.bob.id}/block/"
        )
        unblock_response = self.client.post(
            f"/api/v1/moderation/users/{self.bob.id}/unblock/"
        )

        self.assertEqual(block_response.status_code, status.HTTP_200_OK)
        self.assertEqual(unblock_response.status_code, status.HTTP_200_OK)
        self.bob.refresh_from_db()
        self.assertTrue(self.bob.is_active)

    def test_moderator_cannot_block_self(self):
        self.authenticate(self.moderator)

        response = self.client.post(
            f"/api/v1/moderation/users/{self.moderator.id}/block/"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blocked_user_cannot_create_posts(self):
        self.user.is_active = False
        self.user.save()
        self.authenticate(self.user)

        response = self.client.post(
            "/api/v1/posts/",
            {"content": "Blocked quest."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_blocked_user_cannot_comment_follow_or_like(self):
        self.user.is_active = False
        self.user.save()
        self.authenticate(self.user)

        comment_response = self.client.post(
            f"/api/v1/posts/{self.alice_post.id}/comments/",
            {"content": "Blocked comment."},
            format="json",
        )
        follow_response = self.client.post(
            f"/api/v1/users/{self.alice.id}/follow/"
        )
        like_response = self.client.post(
            f"/api/v1/posts/{self.alice_post.id}/like/"
        )

        self.assertEqual(comment_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(follow_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(like_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_delete_another_users_inappropriate_post(self):
        self.authenticate(self.moderator)

        response = self.client.delete(f"/api/v1/posts/{self.user_post.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.user_post.id).exists())

    def test_root_redirects_to_swagger_ui(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], "/api/docs/")

    def test_openapi_schema_returns_200(self):
        response = self.client.get("/api/schema/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_ui_returns_200(self):
        response = self.client.get(
            "/api/docs/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_returns_200(self):
        response = self.client.get(
            "/api/redoc/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
