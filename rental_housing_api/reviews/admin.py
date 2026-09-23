from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'rating', 'get_tenant_name', 'get_listing_title', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['booking__tenant__name', 'booking__listing__title', 'text']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Отзыв', {
            'fields': ('booking', 'rating', 'text')
        }),
        ('Информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_tenant_name(self, obj):
        return obj.booking.tenant.name
    get_tenant_name.short_description = 'Арендатор'

    def get_listing_title(self, obj):
        return obj.booking.listing.title
    get_listing_title.short_description = 'Объявление'
