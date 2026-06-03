from django.contrib import admin
from .models import Realtor


@admin.register(Realtor)
class RealtorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'is_mvp', 'hire_date')
    list_display_links = ('id', 'name')
    list_filter = ('is_mvp',)
    list_editable = ('is_mvp',)
    search_fields = ('name', 'email')
    list_per_page = 25
