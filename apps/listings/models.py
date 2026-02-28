from django.db import models
from django.conf import settings
from apps.categories.models import Category


class Listing(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активно'),
        ('sold', 'Продано'),
        ('archived', 'В архиве'),
    ]
    CONDITION_CHOICES = [
        ('new', 'Новое'),
        ('used', 'Б/У'),
        ('damaged', 'Требует ремонта'),
    ]

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена')
    is_negotiable = models.BooleanField(default=False, verbose_name='Торг уместен')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='listings',
        verbose_name='Категория'
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='listings', verbose_name='Продавец'
    )
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES,
        default='used', verbose_name='Состояние'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='active', verbose_name='Статус'
    )
    views_count = models.IntegerField(default=0, verbose_name='Просмотры')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE,
        related_name='images', verbose_name='Объявление'
    )
    image = models.ImageField(upload_to='listings/', verbose_name='Изображение')
    order = models.IntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='favorites'
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'listing']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class Message(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE,
        related_name='messages', verbose_name='Объявление'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='sent_messages', verbose_name='Отправитель'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='received_messages', verbose_name='Получатель'
    )
    text = models.TextField(verbose_name='Текст')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
