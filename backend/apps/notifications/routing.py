
# django modules
from django.urls import re_path

# project modules
from apps.notifications import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/notifications/(?P<user_id>\d+)/$", 
        consumers.NotificationConsumer.as_asgi()
    ),
]

