from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg
from datetime import timedelta
from django.utils import timezone

from .models import SearchQuery, ListingView
from .serializers import (
    SearchQuerySerializer, ListingViewSerializer,
    PopularListingSerializer, PopularSearchSerializer
)
from listings.models import Listing
from reviews.models import Review


class AnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def popular_listings(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        listings_with_views = ListingView.objects.filter(
            created_at__gte=start_date
        ).values('listing').annotate(
            views_count=Count('id')
        ).order_by('-views_count')[:10]

        result = []
        for item in listings_with_views:
            listing = Listing.objects.get(id=item['listing'])
            reviews = Review.objects.filter(booking__listing=listing)
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

            result.append({
                'listing_id': listing.id,
                'listing_title': listing.title,
                'views_count': item['views_count'],
                'average_rating': round(avg_rating, 1)
            })

        serializer = PopularListingSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular_searches(self, request):
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        searches = SearchQuery.objects.filter(
            created_at__gte=start_date
        ).values('query_params').annotate(
            search_count=Count('id')
        ).order_by('-search_count')[:10]

        serializer = PopularSearchSerializer(searches, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def listing_stats(self, request):
        listing_id = request.query_params.get('listing_id')
        if not listing_id:
            return Response(
                {'error': 'listing_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        views_count = ListingView.objects.filter(
            listing_id=listing_id,
            created_at__gte=start_date
        ).count()

        reviews = Review.objects.filter(booking__listing_id=listing_id)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        reviews_count = reviews.count()

        return Response({
            'listing_id': listing_id,
            'views_count': views_count,
            'average_rating': round(avg_rating, 1),
            'reviews_count': reviews_count,
            'period_days': days
        })

    @action(detail=False, methods=['post'])
    def log_search(self, request):
        serializer = SearchQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_query = SearchQuery.objects.create(
            user=request.user if request.user.is_authenticated else None,
            query_params=serializer.validated_data['query_params'],
            results_count=serializer.validated_data.get('results_count', 0),
            ip_address=self.get_client_ip(request)
        )

        return Response(
            SearchQuerySerializer(search_query).data,
            status=status.HTTP_201_CREATED
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
