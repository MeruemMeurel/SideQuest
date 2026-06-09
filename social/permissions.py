from rest_framework import permissions


class IsOwnerOrModeratorForDelete(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        is_owner = obj.author_id == request.user.id

        if request.method == "PATCH":
            return is_owner

        if request.method == "DELETE":
            is_moderator = request.user.groups.filter(
                name="moderators",
            ).exists()

            return is_owner or is_moderator

        return False


class IsActiveUserForUnsafeMethods(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
        )


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.groups.filter(name="moderators").exists()
        )
