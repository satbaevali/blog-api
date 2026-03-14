from rest_framework.routers import DefaultRouter
from .views import PostViewSet,CommentViewSet,CategoryViewSet
from apps.blog.stats_view import stats_view
from django.urls import path, include

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("comments", CommentViewSet, basename="comment")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path('stats/', stats_view, name='stats'),
    path("", include(router.urls)),

]