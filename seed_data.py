#!/usr/bin/env python
"""
Скрипт для заполнения базы данных тестовыми данными.
Запуск: python seed_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace.settings')
django.setup()

from apps.users.models import User
from apps.categories.models import Category
from apps.listings.models import Listing

# Категории
categories_data = [
    {'name': 'Электроника', 'slug': 'electronics', 'icon': '📱', 'order': 1, 'children': [
        {'name': 'Телефоны', 'slug': 'phones', 'icon': '📱'},
        {'name': 'Ноутбуки', 'slug': 'laptops', 'icon': '💻'},
        {'name': 'Планшеты', 'slug': 'tablets', 'icon': '📟'},
        {'name': 'ТВ и видео', 'slug': 'tv', 'icon': '📺'},
    ]},
    {'name': 'Одежда и обувь', 'slug': 'clothes', 'icon': '👕', 'order': 2, 'children': [
        {'name': 'Мужская одежда', 'slug': 'mens-clothes', 'icon': '👔'},
        {'name': 'Женская одежда', 'slug': 'womens-clothes', 'icon': '👗'},
        {'name': 'Детская одежда', 'slug': 'kids-clothes', 'icon': '🧒'},
    ]},
    {'name': 'Транспорт', 'slug': 'transport', 'icon': '🚗', 'order': 3, 'children': [
        {'name': 'Автомобили', 'slug': 'cars', 'icon': '🚗'},
        {'name': 'Мотоциклы', 'slug': 'motorcycles', 'icon': '🏍️'},
        {'name': 'Велосипеды', 'slug': 'bikes', 'icon': '🚲'},
    ]},
    {'name': 'Недвижимость', 'slug': 'realty', 'icon': '🏠', 'order': 4, 'children': [
        {'name': 'Квартиры', 'slug': 'apartments', 'icon': '🏢'},
        {'name': 'Дома', 'slug': 'houses', 'icon': '🏡'},
        {'name': 'Аренда', 'slug': 'rent', 'icon': '🔑'},
    ]},
    {'name': 'Мебель и интерьер', 'slug': 'furniture', 'icon': '🛋️', 'order': 5},
    {'name': 'Спорт и отдых', 'slug': 'sport', 'icon': '⚽', 'order': 6},
    {'name': 'Животные', 'slug': 'pets', 'icon': '🐾', 'order': 7},
    {'name': 'Работа', 'slug': 'jobs', 'icon': '💼', 'order': 8},
    {'name': 'Услуги', 'slug': 'services', 'icon': '🔧', 'order': 9},
    {'name': 'Хобби и игры', 'slug': 'hobbies', 'icon': '🎮', 'order': 10},
]

print("Создаём категории...")
for cat_data in categories_data:
    children = cat_data.pop('children', [])
    parent, _ = Category.objects.get_or_create(
        slug=cat_data['slug'], defaults=cat_data
    )
    for child_data in children:
        child_data['parent'] = parent
        Category.objects.get_or_create(slug=child_data['slug'], defaults=child_data)

print(f"Категорий: {Category.objects.count()}")

# Суперпользователь
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Создан admin / admin123")

print("✅ База данных заполнена!")
