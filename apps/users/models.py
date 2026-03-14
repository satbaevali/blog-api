from typing import Any
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _

PREFERRED_LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Русский")),
    ("kk", _("Қазақша")),
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email is required"))
        
        email = self.normalize_email(email)
        # Устанавливаем значения по умолчанию, если они не переданы
        extra_fields.setdefault("is_active", True)
        
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, first_name, last_name, password, **extra_fields)

# Константы вынесены за пределы класса (хорошая практика)
FIRST_NAME_MAX_LENGTH = 50
LAST_NAME_MAX_LENGTH = 50

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=LAST_NAME_MAX_LENGTH)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    
    # Рекомендуется использовать названия из док-строки: created_at, updated_at
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    preferred_language = models.CharField(
        max_length=10,
        choices=PREFERRED_LANGUAGES,
        default="en",
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return f"{self.email} ({self.first_name} {self.last_name})"