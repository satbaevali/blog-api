from decouple import config


ENV_ID_POSIBLE_OPTIONS = ["local", "prod"]
BLOG_ENV_ID = config("BLOG_ENV_ID", cast=str)
SECRET_KEY =  config("SECRET_KEY", cast=str)