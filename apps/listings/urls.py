from django.urls import path
from .views import (
    ListingListView, ListingCreateView, ListingDetailView,
    MyListingsView, FavoriteToggleView, FavoritesListView,
    MessageCreateView, MyMessagesView, SellerListingsView
)

urlpatterns = [
    path('listings/', ListingListView.as_view(), name='listing-list'),
    path('listings/create/', ListingCreateView.as_view(), name='listing-create'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('listings/<int:pk>/favorite/', FavoriteToggleView.as_view(), name='favorite-toggle'),
    path('my/listings/', MyListingsView.as_view(), name='my-listings'),
    path('my/favorites/', FavoritesListView.as_view(), name='my-favorites'),
    path('my/messages/', MyMessagesView.as_view(), name='my-messages'),
    path('messages/', MessageCreateView.as_view(), name='message-create'),
    path('sellers/<int:seller_id>/listings/', SellerListingsView.as_view(), name='seller-listings'),
]
