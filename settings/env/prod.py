# Project modules
from settings.base import *


DEBUG = False
ALLOWED_HOSTS = [
    'luminetwork-backend.azurewebsites.net',
    'localhost',
    '127.0.0.1',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
