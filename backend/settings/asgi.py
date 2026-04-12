# Python modules
import os

# Django modules
from django.core.asgi import get_asgi_application

# Project modules
from settings.conf import BLOG_ENV_ID, ENV_ID_POSSIBLE_OPTIONS

assert BLOG_ENV_ID in ENV_ID_POSSIBLE_OPTIONS, (
    f"Set correct BLOG_ENV_ID env var. Possible options: {ENV_ID_POSSIBLE_OPTIONS}"
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{BLOG_ENV_ID}")

# Important: get_asgi_application() must be called BEFORE importing Channels
django_asgi_app = get_asgi_application()

# Third-party modules
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

# Project modules
from apps.notifications.routing import websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": URLRouter(websocket_urlpatterns),
    }
)