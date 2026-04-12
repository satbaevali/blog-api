#Python modules
import asyncio
import json
import logging
from django.conf import settings

# Third-party modules
import redis

logger = logging.getLogger(__name__)
def published_post_event(post):
    """
    Publish a post published event to Redis channel.

    """

    try:
        redis_host = getattr(settings, "REDIS_HOST", "localhost")
        redis_port = getattr(settings, "REDIS_PORT", 6379)
        redis_db = getattr(settings, "REDIS_DB", 0)

        redis_client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
        )


        event_data = {
            "post_id": post.id,
            "title": post.title,
            "slug": post.slug,
            "author": {
                "id": post.author.id,
                "email": post.author.email,
                "username": post.author.username
            },
            "published_at": post.updated_at.isoformat() if post.updated_at else None,
        }

        message = json.dumps(event_data)
        num_subscribers = redis_client.publish("post_published", message)
        
        logger.info(
            f"Published post published event for post ID {post.id} to Redis channel. Subscribers: {num_subscribers}"

        )
        redis_client.close()
        return num_subscribers
    except Exception as e:
        logger.error(f"Error publishing post published event for post ID {post.id}: {str(e)}")
        return 0
    