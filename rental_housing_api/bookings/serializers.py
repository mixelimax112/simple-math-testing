from rest_framework import serializers
from .models import Booking
from listings.serializers import ListingListSerializer
from django.utils import timezone


class BookingSerializer(serializers.ModelSerializer):
    listing_details = ListingListSerializer(source='listing', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    nights = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_details', 'tenant', 'tenant_name',
            'start_date', 'end_date', 'guests_count', 'status',
            'total_price', 'total_price_currency', 'nights',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'total_price', 'status', 'created_at', 'updated_at']

    def get_nights(self, obj):
        return (obj.end_date - obj.start_date).days

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        guests_count = attrs.get('guests_count')
        listing = attrs.get('listing')

        if end_date <= start_date:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")

        if start_date < timezone.now().date():
            raise serializers.ValidationError("Дата заезда не может быть в прошлом")

        nights = (end_date - start_date).days
        if nights > 30:
            raise serializers.ValidationError("Максимальная длительность бронирования - 30 ночей")

        if guests_count > listing.max_guests:
            raise serializers.ValidationError(
                f"Количество гостей превышает максимум для данного объявления ({listing.max_guests})"
            )

        from listings.models import BlockedDate

        blocked = BlockedDate.objects.filter(
            listing=listing,
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()

        if blocked:
            raise serializers.ValidationError("Выбранные даты заблокированы владельцем")

        overlapping = Booking.objects.filter(
            listing=listing,
            start_date__lt=end_date,
            end_date__gt=start_date,
            status__in=['pending', 'confirmed']
        )

        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError("На выбранные даты уже есть активное бронирование")

        return attrs

    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].user
        return super().create(validated_data)


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['listing', 'start_date', 'end_date', 'guests_count']

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        guests_count = attrs.get('guests_count')
        listing = attrs.get('listing')

        if end_date <= start_date:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")

        if start_date < timezone.now().date():
            raise serializers.ValidationError("Дата заезда не может быть в прошлом")

        nights = (end_date - start_date).days
        if nights > 30:
            raise serializers.ValidationError("Максимальная длительность бронирования - 30 ночей")

        if guests_count > listing.max_guests:
            raise serializers.ValidationError(
                f"Количество гостей превышает максимум ({listing.max_guests})"
            )

        from listings.models import BlockedDate

        blocked = BlockedDate.objects.filter(
            listing=listing,
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()

        if blocked:
            raise serializers.ValidationError("Выбранные даты заблокированы")

        overlapping = Booking.objects.filter(
            listing=listing,
            start_date__lt=end_date,
            end_date__gt=start_date,
            status__in=['pending', 'confirmed']
        ).exists()

        if overlapping:
            raise serializers.ValidationError("На выбранные даты уже есть бронирование")

        return attrs

    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].user
        return super().create(validated_data)


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']

    def validate_status(self, value):
        allowed_statuses = ['confirmed', 'rejected', 'cancelled', 'completed']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Недопустимый статус. Разрешены: {', '.join(allowed_statuses)}")
        return value
