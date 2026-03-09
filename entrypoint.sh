#!/bin/sh

python manage.py migrate

gunicorn settings.wsgi:application --bind 0.0.0.0:8000