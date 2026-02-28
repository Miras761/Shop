from django.contrib import admin
from .models import Listing, ListingImage, Favorite, Message


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'seller', 'price', 'category', 'city', 'status', 'views_count', 'created_at']
    list_filter = ['status', 'condition', 'category']
    search_fields = ['title', 'description', 'seller__username']
    inlines = [ListingImageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'listing', 'is_read', 'created_at']
