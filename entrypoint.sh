#!/bin/sh

cd blogicum

python manage.py makemigrations
python manage.py migrate

gunicorn blogicum.wsgi:application --bind 0.0.0.0:8080