from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action

from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator

import logging
import pytz
from zoneinfo import ZoneInfo
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .models import CustomUser
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    LanguageSerializer, 
    TimezoneSerializer
)

RATE_LIMIT_BODY = {"detail": "Too many requests, please try again later."}
logger = logging.getLogger("users")

class RegisterViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        tags=['auth'],
        summary="User registration",
        request=RegisterSerializer,
        description="Endpoint for user registration. Rate limited to 5 requests per minute per IP.",
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Validation error"),
            429: OpenApiResponse(description="Too many requests")
        },
        examples=[
            OpenApiExample(
                "Successful registration",
                value={
                    'user':{
                        'id': 1,
                        'email': 'user@example.com',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'preferred_language': 'kk',
                        'timezone': 'UTC'
                    },
                    'tokens': {
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWN0aXZhdGlvbiIsInVzZXJfaWQiOjEsImV4cCI6MTY5ODQ3ODQwMCwiaWF0IjoxNjk4NDc0ODAwfQ.abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4NDc4MDAwLCJpYXQiOjE2OTg0NzQ4MDB9.def456ghi789jkl012mno345pqr678stu901vwx234yz567890'
                    }
                }
                    
            )
        ]
    )

    @method_decorator(ratelimit(key="ip", rate="5/m", block=True))
    def create(self, request):
        if getattr(request, "limited", False):
            return Response(RATE_LIMIT_BODY, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        email = request.data.get("email")
        logger.info("Registration attempt for email: %s", email)
        
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Registration failed for %s: %s", email, serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        # ВАЖНО: Отправка письма
        self._send_welcome_email(user)
        
        logger.info("User registered: %s (ID: %s)", user.email, user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _send_welcome_email(self, user: CustomUser):
        # Переключаем контекст на язык пользователя для письма
        with translation.override(user.preferred_language):
            subject = _("Welcome to our Service")
            message = _("Hi {first_name}, thank you for registering!").format(first_name=user.first_name)

            try: 
                send_mail(
                    subject=subject,
                    message=message,
                    recipient_list=[user.email],
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    fail_silently=False,
                )
                logger.info("Welcome email sent to: %s", user.email)
            except Exception as e:  
                logger.error("Failed to send email to %s: %s", user.email, str(e))

class LoginViewSet(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        tags=['auth'],
        summary="User login",
        request=LoginSerializer,
        description="Endpoint for user login. Rate limited to 10 requests per minute per IP.",
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Validation error"),
            429: OpenApiResponse(description="Too many requests")
        },
        examples=[
            OpenApiExample(
                "Successful login",
                value={
                    'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4NDc4MDAwLCJpYXQiOjE2OTg0NzQ4MDB9.def456ghi789jkl012mno345pqr678stu901vwx234yz567890',
                    'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWN0aXZhdGlvbiIsInVzZXJfaWQiOjEsImV4cCI6MTY5ODQ3ODQwMCwiaWF0IjoxNjk4NDc0ODAwfQ.abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890'
                }
            )
        ]
    )

    @method_decorator(ratelimit(key="ip", rate="10/m", block=True))
    def create(self, request):
        if getattr(request, "limited", False):
            return Response(RATE_LIMIT_BODY, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info("Login successful: %s", request.data.get("email"))
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class UserPreferencesViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['preferences'],
        summary="Update language",
        request=LanguageSerializer,
        responses={200: OpenApiResponse(description="Success")}
    )
    @action(detail=False, methods=['patch'], url_path="update-language")
    def update_language(self, request):
        # Используем LanguageSerializer где поле называется 'language'
        serializer = LanguageSerializer(data=request.data)
        if serializer.is_valid():
            new_lang = serializer.validated_data["language"]
            request.user.preferred_language = new_lang
            request.user.save()
            
            # Активируем новый язык сразу для текущего ответа
            translation.activate(new_lang)
            
            logger.info("User %s changed language to %s", request.user.email, new_lang)
            return Response({
                'message': _('Preferred language updated successfully.'),
                'preferred_language': new_lang
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['preferences'],
        summary="Update timezone",
        request=TimezoneSerializer,
        responses={200: OpenApiResponse(description="Success")}
    )
    @action(detail=False, methods=['patch'], url_path="update-timezone")
    def update_timezone(self, request):
        serializer = TimezoneSerializer(data=request.data)
        if serializer.is_valid():
            new_tz = serializer.validated_data["timezone"]
            request.user.timezone = new_tz
            request.user.save()
            
            # Активируем таймзону сразу
            timezone.activate(ZoneInfo(new_tz))
            
            logger.info("User %s changed timezone to %s", request.user.email, new_tz)
            return Response({
                'message': _('Timezone updated successfully.'),
                'timezone': new_tz
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Простые обертки для Token JWT (если используете стандартные)
class TokenObtainPairViewSet(ViewSet):
    permission_classes = [AllowAny]
    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

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
