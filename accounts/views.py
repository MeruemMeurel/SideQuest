from rest_framework import generics, permissions

from django.contrib.auth import get_user_model

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
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = (
        permissions.AllowAny,
    )


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
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


class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_object(self):
        return self.request.user
