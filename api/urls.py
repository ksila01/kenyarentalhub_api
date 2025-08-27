from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, MeView, PropertyViewSet, RentalApplicationViewSet
from .views import PaymentViewSet
from .views import ReviewViewSet
router = DefaultRouter()
router.register(r"properties", PropertyViewSet, basename="property")
router.register(r"applications", RentalApplicationViewSet, basename="application")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("", include(router.urls)),
]

