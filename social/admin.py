from django.contrib import admin

from .models import Comment, Follow, Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "author__username",
        "content",
    )

    list_filter = (
        "created_at",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author",
        "post",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "author__username",
        "post__content",
        "content",
    )

    list_filter = (
        "created_at",
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "follower",
        "followed",
        "created_at",
    )

    search_fields = (
        "follower__username",
        "followed__username",
    )

    list_filter = (
        "created_at",
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "post",
        "created_at",
    )

    search_fields = (
        "user__username",
        "post__content",
    )

    list_filter = (
        "created_at",
    )