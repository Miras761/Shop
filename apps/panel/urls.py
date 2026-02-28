from django.urls import path
from .views import (
    AdminStatsView, AdminUsersView, AdminUserActionView,
    AdminListingsView, AdminListingActionView,
    AdminChatView, AdminDialogMessagesView, UpdateLastSeenView,
    SupportTicketsView, GlobalAnnouncementView, CreateSupportTicketView,
)

urlpatterns = [
    path('stats/', AdminStatsView.as_view()),
    path('users/', AdminUsersView.as_view()),
    path('users/<int:user_id>/action/', AdminUserActionView.as_view()),
    path('listings/', AdminListingsView.as_view()),
    path('listings/<int:listing_id>/action/', AdminListingActionView.as_view()),
    path('chats/', AdminChatView.as_view()),
    path('chats/<int:dialog_id>/', AdminDialogMessagesView.as_view()),
    path('update-seen/', UpdateLastSeenView.as_view()),
    path('support/', SupportTicketsView.as_view()),
    path('support/<int:ticket_id>/', SupportTicketsView.as_view()),
    path('announcement/', GlobalAnnouncementView.as_view()),
    path('create-ticket/', CreateSupportTicketView.as_view()),
]
