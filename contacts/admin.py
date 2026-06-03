from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'listing', 'email', 'phone', 'contact_date', 'user')
    list_display_links = ('id', 'name')
    list_filter = ('contact_date',)
    search_fields = ('name', 'email', 'listing')
    readonly_fields = ('contact_date',)
    list_per_page = 25
