from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Comment, Follow, Like, Post
from .serializers import PostSerializer, CommentSerializer
from .permissions import (
    IsActiveUserForUnsafeMethods,
    IsModerator,
    IsOwnerOrModeratorForDelete,
)


User = get_user_model()

class PostListView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsActiveUserForUnsafeMethods,
    )

    def get_queryset(self):
        return Post.objects.select_related("author").annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrModeratorForDelete,
    )
    http_method_names = (
        'get',
        'patch',
        'delete',
        'head',
        'options',
    )

    def get_queryset(self):
        return Post.objects.select_related("author").annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsActiveUserForUnsafeMethods,
    )

    def get_queryset(self):
        return Comment.objects.select_related("author").filter(post=self.kwargs['post_id'])

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])

        serializer.save(author=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwnerOrModeratorForDelete,
    )
    http_method_names = (
        "patch",
        "delete",
        "options",
    )

    def get_queryset(self):
        return Comment.objects.select_related("author")


class UserPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs["user_id"])

        return Post.objects.select_related("author").filter(author=user).annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )


class FollowView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsActiveUserForUnsafeMethods,
    )

    @extend_schema(request=None, responses={201: OpenApiTypes.OBJECT})
    def post(self, request, user_id):
        followed = get_object_or_404(User, id=user_id)

        if followed.id == request.user.id:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Follow.objects.filter(
            follower=request.user,
            followed=followed,
        ).exists():
            return Response(
                {"detail": "You already follow this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.create(
            follower=request.user,
            followed=followed,
        )

        return Response(
            {
                "id": follow.id,
                "follower": request.user.id,
                "followed": followed.id,
                "created_at": follow.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class UnfollowView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsActiveUserForUnsafeMethods,
    )

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, user_id):
        followed = get_object_or_404(User, id=user_id)
        follow = get_object_or_404(
            Follow,
            follower=request.user,
            followed=followed,
        )
        follow.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsActiveUserForUnsafeMethods,
    )

    @extend_schema(request=None, responses={201: OpenApiTypes.OBJECT})
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        if Like.objects.filter(
            user=request.user,
            post=post,
        ).exists():
            return Response(
                {"detail": "You already like this post."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        like = Like.objects.create(
            user=request.user,
            post=post,
        )

        return Response(
            {
                "id": like.id,
                "user": request.user.id,
                "post": post.id,
                "created_at": like.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class UnlikeView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsActiveUserForUnsafeMethods,
    )

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like = get_object_or_404(
            Like,
            user=request.user,
            post=post,
        )
        like.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_queryset(self):
        followed_user_ids = Follow.objects.filter(
            follower=self.request.user,
        ).values_list("followed_id", flat=True)

        return Post.objects.filter(
            Q(author=self.request.user) | Q(author_id__in=followed_user_ids)
        ).select_related("author").annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        ).order_by("-created_at")


class BlockUserView(APIView):
    permission_classes = (
        IsModerator,
    )

    @extend_schema(request=None, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if user.id == request.user.id:
            return Response(
                {"detail": "Moderators cannot block themselves."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save(update_fields=("is_active",))

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK,
        )


class UnblockUserView(APIView):
    permission_classes = (
        IsModerator,
    )

    @extend_schema(request=None, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save(update_fields=("is_active",))

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK,
        )
