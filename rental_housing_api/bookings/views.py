from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingStatusUpdateSerializer
from core.permissions import IsBookingTenantOrListingOwner, IsTenant


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'listing']

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'update_status':
            return BookingStatusUpdateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_landlord:
            return Booking.objects.filter(listing__owner=user)
        return Booking.objects.filter(tenant=user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsTenant()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsBookingTenantOrListingOwner()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        user = request.user

        if user == booking.listing.owner:
            allowed_statuses = ['confirmed', 'rejected']
        elif user == booking.tenant:
            allowed_statuses = ['cancelled']
        else:
            return Response(
                {'error': 'У вас нет прав для изменения статуса этого бронирования'},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        if new_status not in allowed_statuses:
            return Response(
                {'error': f'Вы можете установить только следующие статусы: {", ".join(allowed_statuses)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = new_status
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        queryset = Booking.objects.filter(tenant=request.user).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def landlord_bookings(self, request):
        if not request.user.is_landlord:
            return Response(
                {'error': 'Доступно только для арендодателей'},
                status=status.HTTP_403_FORBIDDEN
            )
        queryset = Booking.objects.filter(listing__owner=request.user).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
