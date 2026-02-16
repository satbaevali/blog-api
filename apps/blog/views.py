import json
import logging

import redis
from django.conf import settings
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Post, Comment
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer, CommentSerializer

logger = logging.getLogger("blog")

POSTS_LIST_CACHE_KEY = "posts_list_published_v1"
POSTS_LIST_CACHE_TTL = 60  # 60 seconds

RATE_LIMIT_BODY = {"detail": "Too many requests. Try again later."}
REDIS_COMMENTS_CHANNEL = "comments"
REDIS_URL = settings.CACHES["default"]["LOCATION"]

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = (
            Post.objects
            .select_related("author", "category")
            .prefetch_related("tags")
            .order_by("-created_at")
        )
        if self.action in ("list", "retrieve", "comments"):
            return qs.filter(status=Post.Status.PUBLISHED)
        return qs

    def get_permissions(self):
        if self.action in ("list", "retrieve", "comments"):
            return [AllowAny()]
        if self.action in ("create", "add_comment"):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()]

    def list(self, request, *args, **kwargs):
        cached = cache.get(POSTS_LIST_CACHE_KEY)
        if cached is not None:
            return Response(cached, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache.set(POSTS_LIST_CACHE_KEY, response.data, POSTS_LIST_CACHE_TTL)
        return response

    # Rate limit: POST /api/posts/ — max 20 per minute per USER
    @ratelimit(key="user", rate="20/m", block=False)
    def create(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            return Response(RATE_LIMIT_BODY, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            post = serializer.save(author=self.request.user)
        except Exception:
            logger.exception("Post create exception user=%s", getattr(self.request.user, "id", None))
            raise

        cache.delete(POSTS_LIST_CACHE_KEY)
        logger.info("Post created slug=%s by user=%s", post.slug, self.request.user.email)

    def perform_update(self, serializer):
        try:
            post = serializer.save()
        except Exception:
            logger.exception("Post update exception slug=%s", getattr(self.get_object(), "slug", None))
            raise

        cache.delete(POSTS_LIST_CACHE_KEY)
        logger.info("Post updated slug=%s by user=%s", post.slug, self.request.user.email)

    def perform_destroy(self, instance):
        slug = instance.slug
        try:
            instance.delete()
        except Exception:
            logger.exception("Post delete exception slug=%s", slug)
            raise

        cache.delete(POSTS_LIST_CACHE_KEY)
        logger.warning("Post deleted slug=%s by user=%s", slug, self.request.user.email)

    @action(detail=True, methods=["get"], url_path="comments", permission_classes=[AllowAny])
    def comments(self, request, slug=None):
        post = self.get_object()
        qs = post.comments.select_related("author").order_by("-created_at")
        return Response(CommentSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    @comments.mapping.post
    def add_comment(self, request, slug=None):
        post = self.get_object()

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            comment = Comment.objects.create(
                post=post,
                author=request.user,
                body=serializer.validated_data["body"],
            )
        except Exception:
            logger.exception("Comment create exception post_slug=%s user=%s", post.slug, request.user.email)
            raise

        # Pub/Sub event
        r = redis.Redis.from_url(REDIS_URL)
        r.publish(
            REDIS_COMMENTS_CHANNEL,
            json.dumps(
                {
                    "event": "comment_created",
                    "post_slug": post.slug,
                    "comment_id": comment.id,
                    "author_id": request.user.id,
                    "author_email": request.user.email,
                }
            ),
        )

        logger.info("Comment created post=%s comment_id=%s by user=%s", post.slug, comment.id, request.user.email)
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
        logger.info("Comment created comment_id=%s by user=%s", comment.id, self.request.user.email)

    def perform_update(self, serializer):
        comment = serializer.save()
        logger.info("Comment updated comment_id=%s by user=%s", comment.id, self.request.user.email)

    def perform_destroy(self, instance):
        comment_id = instance.id
        try:
            instance.delete()
        except Exception:
            logger.exception("Comment delete exception comment_id=%s", comment_id)
            raise
        logger.warning("Comment deleted comment_id=%s by user=%s", comment_id, self.request.user.email)
