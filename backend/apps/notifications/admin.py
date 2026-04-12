from django.contrib import admin
from django.contrib.admin import ModelAdmin
# Register your models here.
from apps.notifications.models import Notification

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("recipient", "comment", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("recipient__email", "comment__body")
    ordering = ("-created_at",)