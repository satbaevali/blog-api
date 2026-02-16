from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import action 
from rest_framework import status

from .serializers import PostSerializer,CommentSerializer
from .models import Post,Comment
from .permissions import IsAuthorOrReadOnly


class PostViewSet(ViewSet):
    serializer_class = PostSerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = Post.objects.select_related("author", "category").prefetch_related("tags")
        if self.action in ["list", "retrieve"]:
            if not self.request.user.is_authenticated:
                return qs.filter(status=Post.Status.PUBLISHED)
            return qs.filter(status=Post.Status.PUBLISHED) 
        return qs
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
           return [AllowAny()]
        
        if self.action in ("create","add_comment"):
            return [IsAuthorOrReadOnly()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=["get"], url_path="comments", permission_classes=[AllowAny])
    def comments(self, request, slug=None):
        post = self.get_object()
        qs = post.comments.select_related("author").order_by("-created_at")
        serializer = CommentSerializer(data=request.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    @comments.mapping.post
    def add_comment(self, request, slug=None):
        post = self.get_object()
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            body=serializer.validated_data["body"]
        )
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )

class CommentViewSet(ViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.select_related("author", "post").order_by("-created_at")
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()] 
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

