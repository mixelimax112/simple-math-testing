from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Listing, ListingPhoto, BlockedDate
from .serializers import (
    ListingSerializer, ListingCreateSerializer, ListingListSerializer,
    ListingPhotoSerializer, BlockedDateSerializer
)
from core.permissions import IsOwnerOrReadOnly, IsLandlord
from analytics.models import ListingView


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.filter(is_active=True, deleted_at__isnull=True)
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'district', 'housing_type', 'rooms_count']
    search_fields = ['title', 'description', 'city', 'district']
    ordering_fields = ['price', 'created_at', 'rooms_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ListingListSerializer
        elif self.action == 'create':
            return ListingCreateSerializer
        return ListingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        min_guests = self.request.query_params.get('min_guests')

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if min_guests:
            queryset = queryset.filter(max_guests__gte=min_guests)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        ListingView.objects.create(
            listing=instance,
            user=request.user if request.user.is_authenticated else None,
            ip_address=self.get_client_ip(request)
        )

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @action(detail=False, methods=['get'], permission_classes=[IsLandlord])
    def my_listings(self, request):
        queryset = Listing.objects.filter(owner=request.user, deleted_at__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsLandlord])
    def upload_photo(self, request, pk=None):
        listing = self.get_object()
        serializer = ListingPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(listing=listing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsLandlord])
    def block_dates(self, request, pk=None):
        listing = self.get_object()
        serializer = BlockedDateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(listing=listing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ListingPhotoViewSet(viewsets.ModelViewSet):
    queryset = ListingPhoto.objects.all()
    serializer_class = ListingPhotoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            return self.queryset.filter(listing_id=listing_id)
        return self.queryset


class BlockedDateViewSet(viewsets.ModelViewSet):
    queryset = BlockedDate.objects.all()
    serializer_class = BlockedDateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            return self.queryset.filter(listing_id=listing_id)
        return self.queryset
