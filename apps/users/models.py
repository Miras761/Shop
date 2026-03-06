from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    bio = models.TextField(blank=True, verbose_name='О себе')
    rating = models.FloatField(default=0, verbose_name='Рейтинг')
    reviews_count = models.IntegerField(default=0, verbose_name='Кол-во отзывов')
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name='Последний визит')
    is_banned = models.BooleanField(default=False, verbose_name='Заблокирован')
    ban_reason = models.TextField(blank=True, verbose_name='Причина блокировки')
    warnings_count = models.IntegerField(default=0, verbose_name='Предупреждений')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen).seconds < 300
