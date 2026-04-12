from django.shortcuts import render
import logging 
# Create your views here.
#trird-party modules
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

#Project Modules
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.abstract.pagination import DefaultPagination

logger = logging.getLogger(__name__)

class NotificationCountView(APIView):
    """
    Endpoint: GET /api/notifications/count/
    Description: Retrieve the count of unread notifications for the authenticated user.

    Permissions: Requires authentication.
    Response:
        - 200 OK: Returns the count of unread notifications.
        - 204 No Content: If there are no unread notifications.
    
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        logger.info(
            f"Notification count retrieved for user {request.user.email}: {unread_count}"
        )
        return DRFResponse(
            {"unread_count": unread_count}, 
            status=HTTP_200_OK,
        )


class NotificationListView(APIView, DefaultPagination):
    """
    Endpoint: GET /api/notifications/
    Description: Retrieve a paginated list of notifications for the authenticated user.

    Permissions: Requires authentication.
    Response:
        - 200 OK: Returns a paginated list of notifications.
        - 204 No Content: If there are no notifications.
    
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user,
            ).select_related("comment,comment__post, comment__author")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(notifications, request, view=self)
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = NotificationSerializer(notifications, many=True)
        return DRFResponse(
            serializer.data, 
            status=HTTP_200_OK
        )
    
class NotificationMarkReadView(APIView):
    """
    Endpoint: POST /api/notifications/read/
    Description: Mark all notifications as read for the authenticated user.

    Permissions: Requires authentication.
    Response:
        - 200 OK: If notifications were successfully marked as read.
        - 204 No Content: If there are no notifications to mark as read.
    
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        update = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        logger.info(
            f"Marked {update} notifications as read for user {request.user.email}"
        )
        return DRFResponse(
            data = {"marked_read":update},
            status = HTTP_200_OK if update > 0 else HTTP_204_NO_CONTENT
        )