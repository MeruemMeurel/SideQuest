from rest_framework import generics, permissions

from django.contrib.auth import get_user_model
from django.db.models import Count

from .permissions import IsOwnerOrReadOnly
from .serializers import (
    MeSerializer,
    PublicUserSerializer,
    RegisterSerializer,
    UserUpdateSerializer,
)


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (
        permissions.AllowAny,
    )


class UserListView(generics.ListAPIView):
    serializer_class = PublicUserSerializer
    permission_classes = (
        permissions.AllowAny,
    )

    def get_queryset(self):
        return User.objects.annotate(
            posts_count=Count("posts", distinct=True),
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
        )


class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = (
        IsOwnerOrReadOnly,
    )
    http_method_names = (
        "get",
        "patch",
        "head",
        "options",
    )

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return UserUpdateSerializer

        return PublicUserSerializer

    def get_queryset(self):
        return User.objects.annotate(
            posts_count=Count("posts", distinct=True),
            followers_count=Count("followers", distinct=True),
            following_count=Count("following", distinct=True),
        )


class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_object(self):
        return self.request.user
