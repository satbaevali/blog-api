import logging 
from celery import shared_task

from django.core.mail import send_mail
from django.conf import settings

from apps.users.models import CustomUser
logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_welcome_email(self, user_id:int):

    try:
        user = CustomUser.objects.get(id=user_id)
        send_mail(
            subject="Welcome to the Blog API!",
            message=(
                f"Hi {user.first_name},\n\n"
                "Thank you for registering at our Blog API. We're excited to have you on board!\n\n"
                "Best regards,\n"
                "The Blog API Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Welcome email sent to user: {user.email}")
    except CustomUser.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist. Failed to send welcome email.")
    except Exception as e:
        logger.error(f"Failed to send welcome email to user_id {user_id}: {e}", exc_info=True)
        raise
    