# Project modules
from settings.base import *
from decouple import config

DEBUG = False

ALLOWED_HOSTS = [
    'luminetwork-backend.azurewebsites.net',
    'localhost',
    '127.0.0.1',
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT"),
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}
