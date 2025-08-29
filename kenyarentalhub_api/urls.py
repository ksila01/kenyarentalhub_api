from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from api.views import application_update_status

# Import your frontend views
from api.views import register, property_list, property_detail, application_create, property_create, property_review_create,payment_create

# DRF router for backend API
from rest_framework.routers import DefaultRouter
from api.views import (
    PropertyViewSet,
    RentalApplicationViewSet,
    PaymentViewSet,
    ReviewViewSet,
    RegisterView,
    MeView,
)

router = DefaultRouter()
router.register(r"properties", PropertyViewSet, basename="property")
router.register(r"applications", RentalApplicationViewSet, basename="application")
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("admin/", admin.site.urls),

    # Backend API routes (DRF)
    path("api/", include(router.urls)),
    path("api/auth/register/", RegisterView.as_view(), name="auth-register"),
    path("api/auth/login/", include('rest_framework.urls')),
    path("api/auth/me/", MeView.as_view(), name="auth-me"),

    # Frontend pages
    path("", property_list, name="property_list"),
    path("properties/create/", property_create, name="property_create"),
    path("properties/<int:pk>/", property_detail, name="property_detail"),
    path("properties/<int:pk>/apply/", application_create, name="application_create"),
    path("register/", register, name="register"),
    path("login/", LoginView.as_view(template_name='api/login.html'), name='login'),
    path("logout/", LogoutView.as_view(next_page='/login/'), name='logout'),
    path("properties/add/", property_create, name="create_property"),
    path("properties/<int:pk>/reviews/add/", property_review_create, name="property_review_create"),
    path("applications/<int:application_id>/pay/", payment_create, name="payment_create"),
    path("applications/<int:application_id>/status/", application_update_status, name="application_update_status"),



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
