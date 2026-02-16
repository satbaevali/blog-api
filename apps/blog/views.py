from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
import logging 

logger = logging.getLogger("blog")


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = Post.objects.select_related("author", "category").prefetch_related("tags")

        # Public read: only published posts
        if self.action in ("list", "retrieve", "comments"):
            return qs.filter(status=Post.Status.PUBLISHED)

        # Write actions: allow queryset, permission will restrict edits
        return qs

    def get_permissions(self):
        if self.action in ("list", "retrieve", "comments"):
            return [AllowAny()]

        if self.action in ("create", "add_comment"):
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsAuthorOrReadOnly()]

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)

        logger.info(
            "Post created: %s by user %s", 
            post.slug, 
            self.request.user.email,
        )
    def perform_update(self, serializer):
        post = serializer.save()

        logger.info(
            "Post updated: %s by user %s", 
            post.slug, 
            self.request.user.email,
        )
    def perform_destroy(self, instance):
        slug = instance.slug
        instance.delete()

        logger.info(
            "Post deleted: %s by user %s", 
            slug, 
            self.request.user.email,
        )


    @action(detail=True, methods=["get"], url_path="comments", permission_classes=[AllowAny])
    def comments(self, request, slug=None):
        post = self.get_object()
        qs = post.comments.select_related("author").order_by("-created_at")
        return Response(CommentSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @comments.mapping.post
    def add_comment(self, request, slug=None):
        post = self.get_object()

        logger.info(
            "Comment creation attempt on post: %s by user %s", 
            post.slug, 
            request.user.email,
        )

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            body=serializer.validated_data["body"],
        )
        logger.info(
            "Comment created on post: %s by user %s", 
            post.slug, 
            request.user.email,
        )

        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.select_related("author", "post").order_by("-created_at")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()]

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)

        logger.info(
            "Comment created: %s on post %s by user %s", 
            comment.id, 
            comment.post.slug, 
            self.request.user.email,
        )
    
    def perform_update(self, serializer):
        comment = serializer.save()

        logger.info(
            "Comment updated: %s on post %s by user %s", 
            comment.id, 
            comment.post.slug, 
            self.request.user.email,
        )
    def perform_destroy(self, instance):
        comment_id = instance.id
        post_slug = instance.post.slug
        instance.delete()

        logger.info(
            "Comment deleted: %s on post %s by user %s", 
            comment_id, 
            post_slug, 
            self.request.user.email,
        )
