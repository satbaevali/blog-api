# Third-party modules
from rest_framework.routers import DefaultRouter

# Django modules
from django.urls import path, include

# Project modules
from apps.blog.views import PostViewSet, CommentViewSet,post_stream_view

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")


urlpatterns = [
    path("posts/stream/", post_stream_view, name="post-stream"),
    path("", include(router.urls)),
    
]
