#django modules
from django.db.models import (
    Model,
    ForeignKey,

    BooleanField,
    DateTimeField,
    CASCADE,
)
#Project modules
from apps.users.models import CustomUser
from apps.blog.models import Comment

class Notification(Model):
    """Model representing a notification for a user.
    Attributes:
        recipient (ForeignKey): The user who receives the notification.
        sender (ForeignKey): The user who triggered the notification.
        comment (ForeignKey): The comment that triggered the notification.
        message (CharField): A brief message describing the notification.
        is_read (BooleanField): Indicates whether the notification has been read.
        created_at (DateTimeField): The timestamp when the notification was created.
    """
    recipient = ForeignKey(
        to = CustomUser,
        on_delete = CASCADE,
        related_name = "notifications"

    )
    comment = ForeignKey(
        to = Comment,
        on_delete = CASCADE,
        related_name = "notifications"
    )
    is_read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

        def __str__(self):
            return (
                f"Notification for {self.recipient.email}"
                f"on comment: {self.comment.id}"

            )
        
        
