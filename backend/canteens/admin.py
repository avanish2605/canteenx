from django.contrib import admin
from .models import Canteen


@admin.register(Canteen)
class CanteenAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'opening_time', 'closing_time', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'location', 'description')
    readonly_fields = ('created_at', 'updated_at')
