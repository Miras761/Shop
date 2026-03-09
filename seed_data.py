import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace.settings')
django.setup()

from apps.users.models import User
from apps.categories.models import Category
from apps.listings.models import Listing, ListingImage

def seed():
    print("--- Начинаем очистку и заполнение базы ---")
    
    # Создаем категории
    categories = [
        ('Электроника', 'electronics', '📱'),
        ('Одежда', 'clothes', '👕'),
        ('Транспорт', 'transport', '🚗'),
        ('Недвижимость', 'realty', '🏠'),
        ('Дом и Сад', 'home', '🪴'),
    ]
    
    for name, slug, icon in categories:
        Category.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon})
    
    # Создаем админа
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Создан суперпользователь: admin / admin123")

    print("--- База данных готова к работе! ---")

if __name__ == '__main__':
    seed()
