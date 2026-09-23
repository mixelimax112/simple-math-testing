from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsListingOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBookingTenantOrListingOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.tenant == request.user or obj.listing.owner == request.user


class IsReviewAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.booking.tenant == request.user


class IsLandlord(permissions.BasePermission):
    message = 'Только арендодатели могут выполнять это действие'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_landlord


class IsTenant(permissions.BasePermission):
    message = 'Только арендаторы могут выполнять это действие'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'tenant'
