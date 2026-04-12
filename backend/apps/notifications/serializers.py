#trird-party Modules
from rest_framework.serializers import ModelSerializer,DateTimeField,SerializerMethodField

#Project Modules
from apps.notifications.models import Notification


class NotificationSerializer(ModelSerializer):
    """Serializer for the Notification model.
    Serializes the Notification model fields for API responses.
    """
    created_at = DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    comment_body = SerializerMethodField()
    post_slug = SerializerMethodField()
    author_email = SerializerMethodField()
    

    class Meta:
        model = Notification
        fields = [
            "id",
            "comment_body",
            "post_slug",
            "author_email",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["recipient", "comment_body", "post_slug", "author_email"]

        def get_comment_body(self, obj):
            return obj.comment.body
        def get_post_slug(self, obj):
            return obj.comment.post.slug
        def get_author_email(self, obj):
            return obj.comment.author.email
        
