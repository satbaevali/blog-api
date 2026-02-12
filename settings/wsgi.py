import os
from django.core.wsgi import get_wsgi_application
from settings.conf import ENV_ID_POSIBLE_OPTIONS, BLOG_ENV_ID

assert BLOG_ENV_ID in ENV_ID_POSIBLE_OPTIONS, f"BLOG_ENV_ID must be one of {ENV_ID_POSIBLE_OPTIONS}"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{BLOG_ENV_ID}")

application = get_wsgi_application()
