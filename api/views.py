from rest_framework import filters, mixins
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets

from .permissions import IsAuthorOrReadOnly

from .models import Follow, Post, Group, Comment
from .serializers import (CommentSerializer,
                          PostSerializer,
                          GroupSerializer,
                          FollowSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    filter_backends = [filters.SearchFilter]
    filterset_fields = ('group',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        group_id = self.request.query_params.get('group')
        if group_id is None:
            return Post.objects.all()
        group = get_object_or_404(Group, id=group_id)
        return Post.objects.filter(group=group.id)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly)
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class MixinsViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    Класс-заглушка для наследования
    """
    pass


class GroupViewSet(MixinsViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)
    http_method_names = ['get', 'post']
    filter_backends = [filters.SearchFilter]

    def perform_create(self, serializer):
        serializer.save()


class FollowViewSet(MixinsViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__username']
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return Follow.objects.filter(
            following=self.request.user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(
                user=self.request.user,
            )
