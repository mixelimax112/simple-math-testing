from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from djmoney.models.fields import MoneyField
from simple_history.models import HistoricalRecords

from core.models import TimestampedMixin, SoftDeleteMixin, SoftDeleteManager


class Listing(TimestampedMixin, SoftDeleteMixin):
    HOUSING_TYPE_CHOICES = [
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('studio', 'Студия'),
    ]

    owner = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='listings',
        verbose_name='Владелец'
    )
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    city = models.CharField(max_length=100, verbose_name='Город')
    district = models.CharField(max_length=100, verbose_name='Район')
    price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='UAH',
        verbose_name='Цена за ночь'
    )
    rooms_count = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество комнат'
    )
    housing_type = models.CharField(
        max_length=20,
        choices=HOUSING_TYPE_CHOICES,
        verbose_name='Тип жилья'
    )
    max_guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Максимум гостей'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активно')

    objects = SoftDeleteManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        db_table = 'listings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.city}"


class ListingPhoto(TimestampedMixin):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Объявление'
    )
    image = models.ImageField(upload_to='listings/%Y/%m/%d/', verbose_name='Фото')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Фото объявления'
        verbose_name_plural = 'Фото объявлений'
        db_table = 'listing_photos'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Фото {self.order} для {self.listing.title}"


class BlockedDate(TimestampedMixin):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='blocked_dates',
        verbose_name='Объявление'
    )
    start_date = models.DateField(verbose_name='Дата начала блокировки')
    end_date = models.DateField(verbose_name='Дата окончания блокировки')
    reason = models.CharField(max_length=255, blank=True, verbose_name='Причина')

    class Meta:
        verbose_name = 'Заблокированная дата'
        verbose_name_plural = 'Заблокированные даты'
        db_table = 'blocked_dates'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.listing.title}: {self.start_date} - {self.end_date}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date <= self.start_date:
            raise ValidationError('Дата окончания должна быть позже даты начала')
