from .models import CustomUser
from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    CharField,
    ValidationError,
)
import pytz
from rest_framework_simplejwt.tokens import RefreshToken
from .validators import validate_language, validate_timezone    

class RegisterSerializer(ModelSerializer):
    password = CharField(min_length=8, write_only=True)
    password2 = CharField(min_length=8, write_only=True)
    
    # Добавляем валидаторы для проверки при регистрации
    preferred_language = CharField(required=False, validators=[validate_language])
    timezone = CharField(required=False, validators=[validate_timezone])
    
    tokens = SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "preferred_language",
            "timezone",
            "tokens",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Очищаем данные от подтверждения пароля
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        # Используем метод менеджера
        return CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

    def get_tokens(self, obj: CustomUser):
        refresh = RefreshToken.for_user(obj)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

class LoginSerializer(Serializer):
    email = CharField()
    password = CharField(min_length=8, write_only=True)
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = CustomUser.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            # В идеале перевести это сообщение через _()
            raise ValidationError({"detail": "Invalid credentials"})

        refresh = RefreshToken.for_user(user)
        return {
            "email": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

class TimezoneSerializer(serializers.Serializer):
    
    timezone = serializers.CharField(validators=[validate_timezone])

class LanguageSerializer(serializers.Serializer):
    # Если в Postman шлешь {"language": "ru"}, то здесь "language"
    language = serializers.CharField(validators=[validate_language])