import redis
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Listen for comment events from Redis"

    def handle(self, *args, **options):
        r = redis.Redis.from_url(settings.REDIS_URL)
        pubsub = r.pubsub()

        pubsub.subscribe("comments")

        self.stdout.write(self.style.SUCCESS("Listening on Redis channel: comments"))

        for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]

                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                self.stdout.write(data)
