from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='booking.tenant.name', read_only=True)
    listing_title = serializers.CharField(source='booking.listing.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'rating', 'text',
            'tenant_name', 'listing_title', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        booking = attrs.get('booking')
        user = self.context['request'].user

        if booking.status != 'completed':
            raise serializers.ValidationError("Отзыв можно оставить только для завершенного бронирования")

        if booking.tenant != user:
            raise serializers.ValidationError("Вы можете оставить отзыв только на свое бронирование")

        if hasattr(booking, 'review') and self.instance is None:
            raise serializers.ValidationError("Отзыв на это бронирование уже существует")

        existing_reviews = Review.objects.filter(
            booking__listing=booking.listing,
            booking__tenant=user
        )

        if self.instance:
            existing_reviews = existing_reviews.exclude(pk=self.instance.pk)

        if existing_reviews.exists():
            raise serializers.ValidationError("Вы уже оставили отзыв на это объявление")

        return attrs


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'rating', 'text']

    def validate(self, attrs):
        booking = attrs.get('booking')
        user = self.context['request'].user

        if booking.status != 'completed':
            raise serializers.ValidationError("Отзыв можно оставить только для завершенного бронирования")

        if booking.tenant != user:
            raise serializers.ValidationError("Вы можете оставить отзыв только на свое бронирование")

        if hasattr(booking, 'review'):
            raise serializers.ValidationError("Отзыв на это бронирование уже существует")

        return attrs
