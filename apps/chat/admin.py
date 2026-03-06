from django.contrib import admin
from .models import Dialog, ChatMessage, Notification


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['sender', 'text', 'image', 'is_read', 'created_at']


@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ['participant1', 'participant2', 'listing', 'updated_at']
    inlines = [ChatMessageInline]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'text', 'is_read', 'created_at']
    list_filter = ['type', 'is_read']
