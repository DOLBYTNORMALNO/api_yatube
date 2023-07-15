from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.exceptions import NotAuthenticated

from posts.models import Comment, Group, Post
from .serializers import CommentSerializer, GroupSerializer, PostSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Авторизуйтесь, чтобы увидеть посты.")
        return super().get_queryset()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(author=self.request.user)
        else:
            raise NotAuthenticated("Авторизуйтесь, чтобы создать пост.")


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Авторизуйтесь, чтобы увидеть комментарии.")
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        return post.comments.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
            serializer.save(author=self.request.user, post=post)
        else:
            raise NotAuthenticated(
                "Авторизуйтесь, чтобы написать комментарий."
            )


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
