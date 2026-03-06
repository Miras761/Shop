from django.urls import path
from .views import (
    ListingListView, ListingCreateView, ListingDetailView,
    MyListingsView, FavoriteToggleView, FavoritesListView,
    MessageCreateView, MyMessagesView, SellerListingsView,
    ArchiveListingView, MyWarningsView,
    AdminListingListView, AdminDeleteListingView,
    AdminMessagesView, AdminUsersView, AdminSendWarningView, AdminWarningListView,
)

urlpatterns = [
    path('listings/', ListingListView.as_view(), name='listing-list'),
    path('listings/create/', ListingCreateView.as_view(), name='listing-create'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('listings/<int:pk>/favorite/', FavoriteToggleView.as_view(), name='favorite-toggle'),
    path('listings/<int:pk>/archive/', ArchiveListingView.as_view(), name='listing-archive'),
    path('my/listings/', MyListingsView.as_view(), name='my-listings'),
    path('my/favorites/', FavoritesListView.as_view(), name='my-favorites'),
    path('my/messages/', MyMessagesView.as_view(), name='my-messages'),
    path('my/warnings/', MyWarningsView.as_view(), name='my-warnings'),
    path('messages/', MessageCreateView.as_view(), name='message-create'),
    path('sellers/<int:seller_id>/listings/', SellerListingsView.as_view(), name='seller-listings'),
    # Admin endpoints
    path('admin/listings/', AdminListingListView.as_view(), name='admin-listings'),
    path('admin/listings/<int:pk>/delete/', AdminDeleteListingView.as_view(), name='admin-delete-listing'),
    path('admin/messages/', AdminMessagesView.as_view(), name='admin-messages'),
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<int:user_id>/warn/', AdminSendWarningView.as_view(), name='admin-warn'),
    path('admin/warnings/', AdminWarningListView.as_view(), name='admin-warnings'),
]
