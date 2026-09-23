from django.db import models
from django.db.models import JSONField

from core.models import TimestampedMixin


class SearchQuery(TimestampedMixin):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_queries',
        verbose_name='Пользователь'
    )
    query_params = models.JSONField(verbose_name='Параметры поиска')
    results_count = models.PositiveIntegerField(default=0, verbose_name='Количество результатов')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')

    class Meta:
        verbose_name = 'Поисковый запрос'
        verbose_name_plural = 'Поисковые запросы'
        db_table = 'search_queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Поиск от {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ListingView(TimestampedMixin):
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name='Объявление'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='listing_views',
        verbose_name='Пользователь'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP адрес')

    class Meta:
        verbose_name = 'Просмотр объявления'
        verbose_name_plural = 'Просмотры объявлений'
        db_table = 'listing_views'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['listing', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Просмотр {self.listing.title} от {self.created_at.strftime('%Y-%m-%d %H:%M')}"
