from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ListingViewSet, ListingPhotoViewSet, BlockedDateViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'photos', ListingPhotoViewSet, basename='listing-photo')
router.register(r'blocked-dates', BlockedDateViewSet, basename='blocked-date')

urlpatterns = [
    path('', include(router.urls)),
]
