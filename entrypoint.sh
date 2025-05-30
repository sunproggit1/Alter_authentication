#!/bin/bash

# Запуск сервера Django
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000


