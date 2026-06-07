from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
from social.models import Comment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ('created_at',)

    fieldsets = UserAdmin.fieldsets + (
        (
            "SideQuest profile",
            {
                "fields": (
                    "bio",
                    "created_at",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "SideQuest profile",
            {
                "fields": ("bio",),
            },
        ),
    )

    list_display = ('username', 'email', 'is_staff', 'is_active', 'created_at',)

    search_fields = ('username', 'email',)


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