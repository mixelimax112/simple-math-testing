from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Listing, ListingPhoto, BlockedDate


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1
    fields = ['image', 'order']


class BlockedDateInline(admin.TabularInline):
    model = BlockedDate
    extra = 1
    fields = ['start_date', 'end_date', 'reason']


@admin.register(Listing)
class ListingAdmin(SimpleHistoryAdmin):
    list_display = ['title', 'owner', 'city', 'housing_type', 'price', 'is_active', 'created_at']
    list_filter = ['housing_type', 'is_active', 'city', 'created_at']
    search_fields = ['title', 'description', 'city', 'district']
    ordering = ['-created_at']
    inlines = [ListingPhotoInline, BlockedDateInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'title', 'description')
        }),
        ('Местоположение', {
            'fields': ('city', 'district')
        }),
        ('Характеристики', {
            'fields': ('housing_type', 'rooms_count', 'max_guests', 'price')
        }),
        ('Статус', {
            'fields': ('is_active', 'deleted_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'deleted_at']


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ['listing', 'order', 'created_at']
    list_filter = ['created_at']
    ordering = ['listing', 'order']


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ['listing', 'start_date', 'end_date', 'reason']
    list_filter = ['start_date', 'end_date']
    search_fields = ['listing__title', 'reason']
    ordering = ['-start_date']
