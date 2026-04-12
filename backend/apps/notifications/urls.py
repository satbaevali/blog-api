#django modules
from django.urls import path

#Project modules
from apps.notifications.views import (
    NotificationCountView,
    NotificationListView,
    NotificationMarkReadView,
)
urlpatterns = [
    path("notifications/count/", NotificationCountView.as_view(), name="notification-count"),
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/read/", NotificationMarkReadView.as_view(), name="notification-read"),
        
]
