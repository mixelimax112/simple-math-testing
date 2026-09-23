from rest_framework import serializers
from .models import Listing, ListingPhoto, BlockedDate
from django.utils import timezone


class ListingPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ['id', 'image', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class BlockedDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedDate
        fields = ['id', 'start_date', 'end_date', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        if attrs['end_date'] <= attrs['start_date']:
            raise serializers.ValidationError("Дата окончания должна быть позже даты начала")

        if attrs['start_date'] < timezone.now().date():
            raise serializers.ValidationError("Нельзя заблокировать даты в прошлом")

        return attrs


class ListingSerializer(serializers.ModelSerializer):
    photos = ListingPhotoSerializer(many=True, read_only=True)
    blocked_dates = BlockedDateSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price.amount')
    price_currency = serializers.CharField(source='price.currency')

    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'owner_name', 'title', 'description',
            'city', 'district', 'price', 'price_currency',
            'rooms_count', 'housing_type', 'max_guests',
            'is_active', 'photos', 'blocked_dates',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class ListingCreateSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)

    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'city', 'district',
            'price', 'price_currency', 'rooms_count',
            'housing_type', 'max_guests', 'is_active'
        ]

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        price_value = validated_data.pop('price')
        validated_data['price'] = price_value
        return super().create(validated_data)


class ListingListSerializer(serializers.ModelSerializer):
    first_photo = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price.amount', read_only=True)
    price_currency = serializers.CharField(source='price.currency', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'city', 'district', 'price',
            'price_currency', 'housing_type', 'max_guests',
            'first_photo', 'average_rating', 'created_at'
        ]

    def get_first_photo(self, obj):
        photo = obj.photos.first()
        if photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(photo.image.url)
        return None

    def get_average_rating(self, obj):
        from reviews.models import Review
        reviews = Review.objects.filter(booking__listing=obj)
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return None
