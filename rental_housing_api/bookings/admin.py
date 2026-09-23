from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'listing', 'tenant', 'start_date', 'end_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'start_date', 'end_date', 'created_at']
    search_fields = ['listing__title', 'tenant__email', 'tenant__name']
    ordering = ['-created_at']
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Бронирование', {
            'fields': ('listing', 'tenant', 'start_date', 'end_date', 'guests_count')
        }),
        ('Статус и оплата', {
            'fields': ('status', 'total_price', 'total_price_currency')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'total_price']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['listing', 'tenant']
        return self.readonly_fields
