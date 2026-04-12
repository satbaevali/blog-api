# Python modules
import logging

# Third-party modules
from celery import shared_task

# Django modules
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def invalidate_posts_cache(self):
    try:
        cache.delete("published_posts_list")
        logger.info("Published posts cache invalidated via Celery task")
    except Exception as e:
        logger.error(f"Failed to invalidate posts cache: {e}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def publish_scheduled_posts(self):
    from apps.blog.models import Post
    from apps.blog.sse import publish_post_event

    try:
        now = timezone.now()
        scheduled_posts = Post.objects.filter(
            status=Post.Status.SCHEDULED,
            publish_at__lte=now,
        )
        count = scheduled_posts.count()
        if count == 0:
            logger.debug("No scheduled posts to publish")
            return

        for post in scheduled_posts:
            post.status = Post.Status.PUBLISHED
            post.save(update_fields=["status"])
            publish_post_event(post)
            logger.info(f"Auto-published post: post_id={post.id}")

        cache.delete("published_posts_list")
        logger.info(f"Published {count} scheduled posts")
    except Exception as e:
        logger.error(f"Failed to publish scheduled posts: {e}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def generate_daily_stats(self):
    from apps.blog.models import Post, Comment
    from apps.users.models import CustomUser

    try:
        since = timezone.now() - timezone.timedelta(hours=24)
        new_posts = Post.objects.filter(created_at__gte=since).count()
        new_comments = Comment.objects.filter(created_at__gte=since).count()
        new_users = CustomUser.objects.filter(date_joined__gte=since).count()

        logger.info(
            f"Daily stats — new_posts={new_posts}, "
            f"new_comments={new_comments}, "
            f"new_users={new_users}"
        )
    except Exception as e:
        logger.error(f"Failed to generate daily stats: {e}")
        raise