from decouple import config


ENV_ID_POSIBLE_OPTIONS = ["local", "prod"]
ENV_ID = config("DJANGORLAR_ENV_ID", cast=str)
SECRET_KEY = 'SECRET_KEY = "django-insecure-$rwm=hckm==kbug8frdef!3s5!tqa^l@qq$=thc3ukiry11_wd"'