from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLandlord(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "landlord")

class IsTenant(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "tenant")

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and obj.landlord_id == request.user.id)

class IsAuthenticatedPayment(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

