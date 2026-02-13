from apps.users.models import CustomUser
from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
    
    SerializerMethodField,
    CharField,
    ValidationError,
)
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(ModelSerializer):
    password = CharField(
        min_length=8,
        write_only=True
    )

    password2 = CharField(
        min_length=8,
        write_only=True
    )
    tokens = SerializerMethodField(read_only=True)


    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
            "tokens",
        )
    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    def create(self, validated_data):
        return CustomUser.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
    def get_tokens(self, obj:CustomUser):
        refresh = RefreshToken.for_user(obj)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
class LoginSerializer(ModelSerializer):
    email = CharField()
    password = CharField(
        min_length=8,
        write_only=True
    )
    access = CharField(read_only=True)
    refresh = CharField(read_only=True)
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = CustomUser.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise ValidationError(
                {"detail": "Invalid credentials"}
            )
        refresh = RefreshToken.for_user(user)
        return {
            "email": user.email,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }