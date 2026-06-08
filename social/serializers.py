from rest_framework import serializers

from .models import Post

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

