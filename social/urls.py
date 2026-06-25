from django.urls import path

from accounts.views import UserDetailView, UserListView
from .views import (
    BlockUserView,
    CommentListCreateView,
    CommentDetailView,
    FeedView,
    FollowView,
    LikeView,
    PostDetailView,
    PostListView,
    UnblockUserView,
    UnfollowView,
    UnlikeView,
    UserPostListView,
)

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:user_id>/posts/", UserPostListView.as_view(), name="user-post-list"),
    path("users/<int:user_id>/follow/", FollowView.as_view(), name="user-follow"),
    path("users/<int:user_id>/unfollow/", UnfollowView.as_view(), name="user-unfollow"),
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/like/", LikeView.as_view(), name="post-like"),
    path("posts/<int:post_id>/unlike/", UnlikeView.as_view(), name="post-unlike"),
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view(), name="comments-list"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("feed/", FeedView.as_view(), name="feed"),
    path("moderation/users/<int:user_id>/block/", BlockUserView.as_view(), name="user-block"),
    path("moderation/users/<int:user_id>/unblock/", UnblockUserView.as_view(), name="user-unblock"),
]
