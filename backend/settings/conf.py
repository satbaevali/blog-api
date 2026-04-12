"""  
Configuration module for environment settings.

Loads environment-specific configuration using python-decouple.
"""

# Third-party modules
from decouple import config
import os
from pathlib import Path

"""
Environment ID configuration
"""

# Possible environment options
ENV_ID_POSSIBLE_OPTIONS = ("local", "prod")
BLOG_ENV_ID = config("BLOG_ENV_ID", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)

#REdis URLS
BLOG_REDIS_URL = config("BLOG_REDIS_URL", default = "redis://localhost:6379/0")
BLOG_CELERY_BROKER_URL = config(
    "BLOG_CELERY_BROKER_URL", 
    default = "redis://localhost:6379/0"
)
#FLOWER URLS
BLOG_FLOWER_USER = config("BLOG_FLOWER_USER", default = "admin")
BLOG_FLOWER_PASSWORD = config("BLOG_FLOWER_PASSWORD", default = "change_me")

# Current environment ID from environment variable


# Django secret key from environment variable

"""  
Configuration module for environment settings.

Loads environment-specific configuration using python-decouple.
"""

# Third-party modules
from decouple import config
import os

"""
Environment ID configuration
"""

# Possible environment options
ENV_ID_POSSIBLE_OPTIONS = ("local", "prod")
BLOG_ENV_ID = config("BLOG_ENV_ID", cast=str)
SECRET_KEY = config("SECRET_KEY", cast=str)

#REdis URLS
BLOG_REDIS_URL = config("BLOG_REDIS_URL", default = "redis://localhost:6379/0")
BLOG_CELERY_BROKER_URL = config(
    "BLOG_CELERY_BROKER_URL", 
    default = "redis://localhost:6379/0"
)
#FLOWER URLS
BLOG_FLOWER_USER = config("BLOG_FLOWER_USER", default = "admin")
BLOG_FLOWER_PASSWORD = config("BLOG_FLOWER_PASSWORD", default = "change_me")

# Current environment ID from environment variable


# Django secret key from environment variable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
