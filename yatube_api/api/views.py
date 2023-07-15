from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.exceptions import NotAuthenticated
from posts.models import Post, Comment, Group
from .serializers import PostSerializer, CommentSerializer, GroupSerializer

from rest_framework import permissions


class IsAuthorOrDeny(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to view, edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the author of the post.
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrDeny]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            raise NotAuthenticated("You must be authenticated to create a post.")


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrDeny]  # Изменено здесь

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        return post.comments.all()

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
