#!/usr/bin/env bash
# exit on error
set -o errexit

# Установка зависимостей
pip install -r requirements.txt

# Принудительное создание миграций для всех приложений
# Это исправит ошибки 500, так как таблицы будут соответствовать коду
python manage.py makemigrations users
python manage.py makemigrations categories
python manage.py makemigrations listings

# Применяем миграции к базе данных Render
python manage.py migrate

# Собираем статические файлы для WhiteNoise
python manage.py collectstatic --no-input

# Заполняем базу категориями (если их нет)
python seed_data.py
