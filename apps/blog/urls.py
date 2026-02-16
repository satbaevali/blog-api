from rest_framework.routers import DefaultRouter
from .views import PostViewSet,CommentViewSet 

router = DefaultRouter()
router.register("posts", PostViewSet, basename="post")
router.register("comments", CommentViewSet, basename="comment")

urlpatterns = router.urls