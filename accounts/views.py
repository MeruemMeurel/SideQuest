from rest_framework import generics, permissions

from django.contrib.auth import get_user_model

from .permissions import IsOwnerOrReadOnly
from .serializers import RegisterSerializer, UserSerializer


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (
        permissions.AllowAny,
    )


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        permissions.AllowAny,
    )


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (
        IsOwnerOrReadOnly,
    )
    http_method_names = (
        "get",
        "patch",
        "head",
        "options",
    )
