from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("created_at",)

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

    list_display = (
        "username",
        "email",
        "is_staff",
        "is_active",
        "created_at",
    )

    search_fields = (
        "username",
        "email",
    )