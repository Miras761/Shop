from django.db import models
from django.conf import settings


class Dialog(models.Model):
    """Диалог между двумя пользователями (опционально привязан к объявлению)"""
    participant1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='dialogs_as_p1'
    )
    participant2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='dialogs_as_p2'
    )
    listing = models.ForeignKey(
        'listings.Listing', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dialogs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['participant1', 'participant2', 'listing']]
        ordering = ['-updated_at']
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'

    def get_other_participant(self, user):
        return self.participant2 if self.participant1 == user else self.participant1

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def __str__(self):
        return f"Диалог {self.participant1} ↔ {self.participant2}"


class ChatMessage(models.Model):
    dialog = models.ForeignKey(
        Dialog, on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    text = models.TextField(blank=True, verbose_name='Текст')
    image = models.ImageField(
        upload_to='chat_images/', blank=True, null=True,
        verbose_name='Изображение'
    )
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"{self.sender}: {self.text[:40] or '[фото]'}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('message', 'Новое сообщение'),
        ('listing_sold', 'Объявление продано'),
        ('new_listing', 'Новое объявление'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    text = models.CharField(max_length=255)
    dialog = models.ForeignKey(
        Dialog, on_delete=models.CASCADE,
        null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'


class SupportTicket(models.Model):
    STATUS_CHOICES = [('open', 'Открыт'), ('closed', 'Закрыт')]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='support_tickets', null=True, blank=True
    )
    email = models.EmailField(blank=True, verbose_name='Email')
    subject = models.CharField(max_length=200, verbose_name='Тема')
    message = models.TextField(verbose_name='Сообщение')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Тикет поддержки'
        verbose_name_plural = 'Тикеты поддержки'


class GlobalAnnouncement(models.Model):
    text = models.TextField(verbose_name='Текст')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['-created_at']
