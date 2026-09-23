from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from djmoney.models.fields import MoneyField
from simple_history.models import HistoricalRecords

from core.models import TimestampedMixin, SoftDeleteMixin, SoftDeleteManager


class Booking(TimestampedMixin, SoftDeleteMixin):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
        ('rejected', 'Отклонено'),
        ('expired', 'Истекло'),
    ]

    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Объявление'
    )
    tenant = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='bookings',
        verbose_name='Арендатор'
    )
    start_date = models.DateField(verbose_name='Дата заезда')
    end_date = models.DateField(verbose_name='Дата выезда')
    guests_count = models.PositiveIntegerField(verbose_name='Количество гостей')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    total_price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='UAH',
        verbose_name='Общая стоимость'
    )

    objects = SoftDeleteManager()
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        db_table = 'bookings'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F('start_date')),
                name='end_date_after_start_date'
            ),
        ]
        indexes = [
            models.Index(fields=['listing', 'start_date', 'end_date']),
            models.Index(fields=['tenant', 'status']),
        ]

    def __str__(self):
        return f"Бронь #{self.pk} - {self.listing.title} ({self.start_date} - {self.end_date})"

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError('Дата выезда должна быть позже даты заезда')

        if self.start_date < timezone.now().date():
            raise ValidationError('Дата заезда не может быть в прошлом')

        nights = (self.end_date - self.start_date).days
        if nights > 30:
            raise ValidationError('Максимальная длительность бронирования - 30 ночей')

        if self.guests_count > self.listing.max_guests:
            raise ValidationError(
                f'Количество гостей превышает максимум для данного объявления ({self.listing.max_guests})'
            )

        self._check_date_overlap()

    def _check_date_overlap(self):
        from listings.models import BlockedDate

        blocked = BlockedDate.objects.filter(
            listing=self.listing,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exists()

        if blocked:
            raise ValidationError('Выбранные даты заблокированы владельцем')

        overlapping = Booking.objects.filter(
            listing=self.listing,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
            status__in=['pending', 'confirmed']
        )

        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError('На выбранные даты уже есть активное бронирование')

    def save(self, *args, **kwargs):
        if not self.total_price:
            nights = (self.end_date - self.start_date).days
            self.total_price = self.listing.price * nights
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        nights = (self.end_date - self.start_date).days
        return self.listing.price * nights
