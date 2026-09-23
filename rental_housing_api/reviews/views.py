from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from core.permissions import IsReviewAuthor


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['booking__listing']

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsReviewAuthor()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            queryset = queryset.filter(booking__listing_id=listing_id)
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        queryset = Review.objects.filter(booking__tenant=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
