from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from core.models import TimestampedMixin


class Review(TimestampedMixin):
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Бронирование'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Рейтинг'
    )
    text = models.TextField(verbose_name='Текст отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        db_table = 'reviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking']),
        ]

    def __str__(self):
        return f"Отзыв от {self.booking.tenant.name} - {self.rating}/5"

    def clean(self):
        if self.booking.status != 'completed':
            raise ValidationError('Отзыв можно оставить только для завершенного бронирования')

        if self.booking.tenant != self.booking.tenant:
            raise ValidationError('Отзыв может оставить только арендатор')

        existing_reviews = Review.objects.filter(
            booking__listing=self.booking.listing,
            booking__tenant=self.booking.tenant
        )

        if self.pk:
            existing_reviews = existing_reviews.exclude(pk=self.pk)

        if existing_reviews.exists():
            raise ValidationError('Вы уже оставили отзыв на это объявление')
