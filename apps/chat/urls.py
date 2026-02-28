from django.urls import path
from .views import (
    DialogListView, DialogStartView,
    DialogMessagesView, SendMessageView,
    NotificationsView, UnreadCountView, MarkNotificationsReadView,
)

urlpatterns = [
    path('dialogs/', DialogListView.as_view(), name='dialog-list'),
    path('dialogs/start/', DialogStartView.as_view(), name='dialog-start'),
    path('dialogs/<int:dialog_id>/messages/', DialogMessagesView.as_view(), name='dialog-messages'),
    path('dialogs/<int:dialog_id>/send/', SendMessageView.as_view(), name='send-message'),
    path('notifications/', NotificationsView.as_view(), name='notifications'),
    path('notifications/read/', MarkNotificationsReadView.as_view(), name='notifications-read'),
    path('unread/', UnreadCountView.as_view(), name='unread-count'),
]
