from rest_framework import generics, permissions

from .models import Post
from .serializers import PostSerializer
from .permissions import IsOwnerOrModeratorForDelete

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrModeratorForDelete,
    )
    http_method_names = (
        'get',
        'patch',
        'delete',
        'head',
        'options',
    )