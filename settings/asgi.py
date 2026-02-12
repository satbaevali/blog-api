import os
from django.core.asgi import get_asgi_application
from settings.conf import ENV_ID_POSIBLE_OPTIONS, BLOG_ENV_ID

# Проверка, что BLOG_ENV_ID корректен
assert BLOG_ENV_ID in ENV_ID_POSIBLE_OPTIONS, f"BLOG_ENV_ID must be one of {ENV_ID_POSIBLE_OPTIONS}"

# Устанавливаем настройки для Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{BLOG_ENV_ID}")

application = get_asgi_application()
