import logging

from celery import shared_task

from apps.blog.models import Comment
from apps.notifications.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer



logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def process_new_comment_notification(self, comment_id:int):
    try:
        comment =Comment.objects.select_related(
            "post", "post_author", "author"
        ).get(id=comment_id)
    except Comment.DoesNotExist:
        logger.error(f"Comment with id {comment_id} does not exist. Cannot create notification.")
        return
    
    try:
        post_author = comment.post_author
        if comment.author != post_author:
            Notification.objects.create(
                recipient=post_author,
                comment=comment,
            )
            logger.info(
                f"Notification created for user {post_author.email} "
                f"on comment {comment.id}"
            )
        channel_layer = get_channel_layer()
        group_name = f"post_{comment.post.slug}_comments"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "new_comment_notification",
                "comment_id": comment.id,
                "author":{
                    "id": comment.author.id,
                    "email": comment.author.email,
                    "first_name": comment.author.first_name,
                    "last_name": comment.author.last_name,
                },
                "body": comment.body,
                "created_at": comment.created_at.isoformat() if comment.created_at else None,
            }
        )
        logger.info(
            f"Sent new comment notification to group {group_name} for comment {comment.id}"
        )
    except Exception as e:
        logger.error(f"Failed to process new comment notification for comment_id {comment_id}: {e}", exc_info=True)
        raise

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def clear_expired_notifications(self):
    from django.utils import timezone
    try:
        cutoff = timezone.now() - timezone.timedelta(days=30)
        deleted_count, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
        logger.info(f"Cleared {deleted_count} expired notifications")
    except Exception as e:
        logger.error(f"Failed to clear expired notifications: {e}", exc_info=True)
        raise