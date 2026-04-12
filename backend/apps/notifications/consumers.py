# Python modules
import json
import logging

# Third-party modules
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

# Django modules
from django.contrib.auth.models import AnonymousUser

# Third-party modules
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)


class CommentConsumer(AsyncWebsocketConsumer):
    """
    Async WebSocket consumer for live comment feed on a post.

    Connection URL: ws://<host>/ws/posts/<slug>/comments/?token=<access_token>

    - Authenticates user via JWT token passed as query parameter.
    - Rejects unauthenticated connections with close code 4001.
    - Rejects connections for non-existent posts with close code 4004.
    - Joins a Channels group for the post and receives new comment events.
    """

    async def connect(self):
        self.slug = self.scope["url_route"]["kwargs"]["slug"]
        self.group_name = f"post_{self.slug}_comments"

        # --- Step 1: Authenticate via JWT query param ---
        user = await self.get_user_from_token()
        if user is None:
            logger.warning(
                f"WebSocket rejected (4001): unauthenticated, slug={self.slug}"
            )
            await self.close(code=4001)
            return

        self.user = user

        # --- Step 2: Check post exists ---
        post_exists = await self.check_post_exists(self.slug)
        if not post_exists:
            logger.warning(
                f"WebSocket rejected (4004): post not found, slug={self.slug}"
            )
            await self.close(code=4004)
            return

        # --- Step 3: Join the group ---
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()
        logger.info(
            f"WebSocket connected: user_id={self.user.id}, slug={self.slug}"
        )

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )
        logger.info(
            f"WebSocket disconnected: slug={self.slug}, code={close_code}"
        )

    async def receive(self, text_data=None, bytes_data=None):
        # Clients don't send messages — this is a one-way feed (server → client)
        pass

    async def new_comment(self, event):
        """
        Handler called when a message is sent to the group.
        Forwards the comment data to the WebSocket client.

        Expected event format:
        {
            "type": "new_comment",
            "comment_id": int,
            "author": {"id": int, "email": str},
            "body": str,
            "created_at": str (ISO format)
        }
        """
        await self.send(
            text_data=json.dumps(
                {
                    "comment_id": event["comment_id"],
                    "author": event["author"],
                    "body": event["body"],
                    "created_at": event["created_at"],
                }
            )
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    async def get_user_from_token(self):
        """
        Extracts JWT access token from query string and returns the user.
        Returns None if token is missing or invalid.
        """
        from apps.users.models import CustomUser

        query_string = self.scope.get("query_string", b"").decode()
        params = dict(
            pair.split("=") for pair in query_string.split("&") if "=" in pair
        )
        token_str = params.get("token")

        if not token_str:
            return None

        try:
            token = AccessToken(token_str)
            user_id = token["user_id"]
            user = await database_sync_to_async(CustomUser.objects.get)(id=user_id)
            return user
        except (TokenError, InvalidToken, Exception) as e:
            logger.warning(f"JWT WebSocket auth failed: {e}")
            return None

    @database_sync_to_async
    def check_post_exists(self, slug):
        """
        Checks whether a post with the given slug exists in the database.
        """
        from apps.blog.models import Post
        return Post.objects.filter(slug=slug).exists()