from rest_framework import serializers
from .models import SearchQuery, ListingView


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ['id', 'query_params', 'results_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class ListingViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingView
        fields = ['id', 'listing', 'created_at']
        read_only_fields = ['id', 'created_at']


class PopularListingSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField()
    listing_title = serializers.CharField()
    views_count = serializers.IntegerField()
    average_rating = serializers.FloatField()


class PopularSearchSerializer(serializers.Serializer):
    query_params = serializers.JSONField()
    search_count = serializers.IntegerField()
