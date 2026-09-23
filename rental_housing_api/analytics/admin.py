from django.contrib import admin

from .models import SearchQuery, ListingView


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'results_count', 'ip_address', 'created_at']
    list_filter = ['created_at', 'results_count']
    search_fields = ['user__email', 'ip_address']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Поисковый запрос', {
            'fields': ('user', 'query_params', 'results_count', 'ip_address')
        }),
        ('Информация', {
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ['created_at']


@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    list_display = ['id', 'listing', 'user', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['listing__title', 'user__email', 'ip_address']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Просмотр', {
            'fields': ('listing', 'user', 'ip_address')
        }),
        ('Информация', {
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ['created_at']
