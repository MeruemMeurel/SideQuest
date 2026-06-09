from rest_framework import serializers

from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "author",
            "created_at",
            "updated_at",
        )

    def validate_content (self, value):
        if not value.strip():
            raise serializers.ValidationError("Post must not be empty")

        return value


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment

        fields = (
            "id",
            "author",
            "post",
            "content",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author",
            "post",
            "created_at",
            "updated_at",
        )

    def validate_content (self, value):
        if not value.strip():
            raise serializers.ValidationError("Comment cannot be empty")
        return value

