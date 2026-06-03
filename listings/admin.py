from django.contrib import admin
from .models import Listing, Favourite


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'state', 'price', 'bedrooms', 'is_published', 'list_date', 'realtor')
    list_display_links = ('id', 'title')
    list_filter = ('is_published', 'state', 'realtor')
    list_editable = ('is_published',)
    search_fields = ('title', 'description', 'address', 'city', 'state', 'zipcode')
    list_per_page = 25
    readonly_fields = ('list_date',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'listing__title')
    list_per_page = 25
