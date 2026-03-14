from decouple import config
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


ENV_ID_POSIBLE_OPTIONS = ["local", "prod"]
BLOG_ENV_ID = config("BLOG_ENV_ID", cast=str)
SECRET_KEY =  config("SECRET_KEY", cast=str)

REDIS_URL = config(
    "REDIS_URL", 
    default="redis://localhost:6379/1",
    cast=str
)
# Папка для collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Папки, где Django ищет исходные статические файлы
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]