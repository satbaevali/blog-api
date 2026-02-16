from django.shortcuts import render

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer

from rest_framework import status
import logging

logger = logging.getLogger("users")

class RegisterViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request):
        email = request.data.get("email")
        logger.info (
            "Registration attempt for email: %s", email
        )
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning (
                "Registration failed for email: %s - Errors: %s", email, serializer.errors
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        logger.info (
            "Registration successful for email: %s - User ID: %s", email, user.id
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class TokenViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
class TokenRefreshViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
class TokenObtainPairViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer



    def create(self, request):
        email = request.data.get("email")
        logger.info (
            "Token obtain attempt for email: %s", email
        )
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            logger.warning (
                "Token obtain failed for email: %s - Errors: %s", email, serializer.errors
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        logger.info (
            "Token obtain successful for email: %s", 
            email
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    
    
class LoginViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def create(self, request):
        email = request.data.get("email")
        logger.info (
            "Login attempt for email: %s", email
        )
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning (
                "Login failed for email: %s - Errors: %s", email, serializer.errors
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        logger.info (
            "Login successful for email: %s", email
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)