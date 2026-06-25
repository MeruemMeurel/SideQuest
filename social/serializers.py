from drf_spectacular.utils import OpenApiTypes, extend_schema_field
from rest_framework import serializers

from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True,
    )
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "author_username",
            "content",
            "likes_count",
            "comments_count",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "author",
            "author_username",
            "likes_count",
            "comments_count",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(OpenApiTypes.INT)
    def get_likes_count(self, obj):
        return getattr(obj, "likes_count", obj.likes.count())

    @extend_schema_field(OpenApiTypes.INT)
    def get_comments_count(self, obj):
        return getattr(obj, "comments_count", obj.comments.count())

    def validate_content (self, value):
        if not value.strip():
            raise serializers.ValidationError("Post must not be empty")

        return value


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = Comment

        fields = (
            "id",
            "author",
            "author_username",
            "post",
            "content",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "author_username",
            "post",
            "created_at",
            "updated_at",
        )

    def validate_content (self, value):
        if not value.strip():
            raise serializers.ValidationError("Comment cannot be empty")
        return value

