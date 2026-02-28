#!/usr/bin/env bash
# Скрипт сборки для Render
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python seed_data.py
