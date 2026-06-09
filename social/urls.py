from django.urls import path

from .views import PostListView, PostDetailView
from .views import (
    CommentListCreateView,
    PostDetailView,
    PostListView,
)

urlpatterns = [
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view(), name="comments-list"),
]