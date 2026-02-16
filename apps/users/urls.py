from django.urls import path, include
from .views import RegisterViewSet,TokenRefreshViewSet,TokenViewSet,LoginViewSet,TokenObtainPairViewSet

urlpatterns = [
    path("register/", RegisterViewSet.as_view({"post": "create"}), name="register"),
    path("login/", LoginViewSet.as_view({"post": "create"}), name="login"),
    path("token/", TokenViewSet.as_view({"post": "create"}), name ="token"),
    path("token/refresh/", TokenRefreshViewSet.as_view({"post": "create"}), name="token_refresh"),
    path("token/obtain/", TokenObtainPairViewSet.as_view({"post": "create"}), name="token_obtain_pair"),
]
