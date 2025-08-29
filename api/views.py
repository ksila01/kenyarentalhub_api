from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Avg, Count

from .models import Property, RentalApplication, Payment, Review
from .forms import UserRegisterForm, PropertyForm
from .serializers import (
    UserSerializer,
    PropertySerializer,
    RentalApplicationSerializer,
    PaymentSerializer,
    ReviewSerializer
)
from .permissions import IsLandlord, IsTenant, IsOwnerOrReadOnly
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------------------------
# Frontend Function-Based Views
# ---------------------------
def property_list(request):
    properties = Property.objects.filter(is_available=True)
    return render(request, 'api/property_list.html', {'properties': properties})

def property_detail(request, pk):
    # Get the property object or return a 404 if not found
    property_obj = get_object_or_404(Property, pk=pk)

    error = None
    if request.method == 'POST':
        # Handle rental application submit (tenants only)
        if not request.user.is_authenticated or getattr(request.user, "role", None) != "tenant":
            return redirect('login')
        message = (request.POST.get('message') or '').strip()
        try:
            RentalApplication.objects.create(property=property_obj, tenant=request.user, message=message)
            messages.success(request, "Application submitted.")
            return redirect('property_detail', pk=pk)  # Redirect to the current property detail page
        except IntegrityError:
            error = 'You have already applied for this property.'

    # ---- Reviews context ----
    reviews_qs = property_obj.reviews.select_related('tenant').order_by('-created_at')
    agg = reviews_qs.aggregate(avg=Avg('rating'), count=Count('id'))
    user_has_reviewed = (
        request.user.is_authenticated
        and Review.objects.filter(property=property_obj, tenant=request.user).exists()
    )

    # ---- Current user's application & payment (for payment CTA) ----
    user_application = None
    user_payment = None
    if request.user.is_authenticated and getattr(request.user, "role", None) == "tenant":
        user_application = (RentalApplication.objects
                            .filter(property=property_obj, tenant=request.user)
                            .order_by('-created_at')
                            .first())
        if user_application:
            user_payment = (Payment.objects
                            .filter(application=user_application)
                            .order_by('-created_at')
                            .first())

    # ---- Pass landlord applications ----
    landlord_applications = None
    if request.user.is_authenticated and getattr(request.user, "role", None) == "landlord" and property_obj.landlord_id == request.user.id:
        landlord_applications = property_obj.applications.select_related('tenant').order_by('-created_at')

    # Add all the required context to the dictionary
    context = {
        'property': property_obj,
        'error': error,
        'reviews': reviews_qs,
        'review_count': agg['count'] or 0,
        'avg_rating': agg['avg'] or 0,
        'user_has_reviewed': user_has_reviewed,
        'user_application': user_application,
        'user_payment': user_payment,
        'landlord_applications': landlord_applications,  # Add landlord applications context
    }

    return render(request, 'api/property_detail.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('property_list')
    else:
        form = UserRegisterForm()
    return render(request, 'api/register.html', {'form': form})

@login_required
def application_create(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        message = request.POST.get('message')
        try:
            RentalApplication.objects.create(
                property=property_obj,
                tenant=request.user,
                message=message
            )
            return redirect('property_list')
        except IntegrityError:
            return render(request, 'api/application_form.html', {
                'property': property_obj,
                'error': 'You have already applied for this property.'
            })
    return render(request, 'api/application_form.html', {'property': property_obj})

@login_required
def property_create(request):
    if getattr(request.user, "role", None) != "landlord":
        return redirect('property_list')
    if request.method == "POST":
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.landlord = request.user
            prop.save()
            return redirect('property_detail', pk=prop.pk)
    else:
        form = PropertyForm()
    return render(request, 'api/property_create.html', {'form': form})

# ---------------------------
# Backend API Views (DRF)
# ---------------------------
class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class LoginView(DjangoLoginView):
    template_name = 'api/login.html'

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by("-created_at")
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsLandlord()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [AllowAny()]

    def perform_create(self, serializer):
        # landlord must be the authenticated user
        serializer.save(landlord=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        q = p.get("q")
        category = p.get("category")
        location = p.get("location")
        min_price = p.get("min_price")
        max_price = p.get("max_price")
        is_available = p.get("is_available")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q))
        if category:
            qs = qs.filter(category__iexact=category)
        if location:
            qs = qs.filter(location__icontains=location)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if is_available in ("true", "false"):
            qs = qs.filter(is_available=(is_available == "true"))
        return qs

class RentalApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = RentalApplicationSerializer
    queryset = RentalApplication.objects.select_related("property", "tenant").all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsTenant()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if not user.is_authenticated:
            return qs.none()
        if user.role == "tenant":
            return qs.filter(tenant=user).order_by("-created_at")
        if user.role == "landlord":
            return qs.filter(property__landlord=user).order_by("-created_at")
        return qs.none()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user.role != "landlord" or instance.property.landlord_id != user.id:
            return Response({"detail": "Only the property landlord can update this application."},
                            status=status.HTTP_403_FORBIDDEN)
        allowed = {"status"}
        data = {k: v for k, v in request.data.items() if k in allowed}
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.select_related("application", "application__tenant", "application__property").all()

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsTenant()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        application = serializer.validated_data["application"]
        if application.tenant != self.request.user:
            raise PermissionDenied("You can only pay for your own applications.")
        serializer.save()

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related("property", "tenant").all()

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsTenant()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)
@login_required
def property_review_create(request, pk):
    from .models import Property, Review  # local import avoids any weird import order issues
    property_obj = get_object_or_404(Property, pk=pk)

    if request.method != 'POST':
        return redirect('property_detail', pk=pk)

    # Only tenants can leave reviews
    if getattr(request.user, "role", None) != "tenant":
        messages.error(request, "Only tenants can leave reviews.")
        return redirect('property_detail', pk=pk)

    rating_raw = request.POST.get('rating')
    comment = (request.POST.get('comment') or '').strip()

    # Validate rating
    try:
        rating = int(rating_raw)
    except (TypeError, ValueError):
        messages.error(request, "Rating must be an integer between 1 and 5.")
        return redirect('property_detail', pk=pk)

    if rating < 1 or rating > 5:
        messages.error(request, "Rating must be an integer between 1 and 5.")
        return redirect('property_detail', pk=pk)

    try:
        Review.objects.create(property=property_obj, tenant=request.user, rating=rating, comment=comment)
        messages.success(request, "Thanks for your review!")
    except IntegrityError:
        messages.error(request, "You’ve already reviewed this property.")

    return redirect('property_detail', pk=pk)

@login_required
def payment_create(request, application_id):
    application = get_object_or_404(RentalApplication, pk=application_id)

    # Must be the tenant on this application
    if application.tenant_id != request.user.id:
        messages.error(request, "You can only pay for your own applications.")
        return redirect('property_detail', pk=application.property_id)

    # Require approval
    if application.status != "approved":
        messages.error(request, "Payment is only available after your application is approved.")
        return redirect('property_detail', pk=application.property_id)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.application = application
            # Leave status = 'pending' (default). In a real gateway, you’d update to 'completed' on success.
            payment.save()
            messages.success(request, "Payment submitted. Status: pending.")
            return redirect('property_detail', pk=application.property_id)
    else:
        form = PaymentForm()

    return render(request, 'api/payment_create.html', {
        'form': form,
        'application': application,
    })

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import RentalApplication

@login_required
@require_POST
def application_update_status(request, application_id):
    app = get_object_or_404(RentalApplication, pk=application_id)

    # Only the property’s landlord can update
    if getattr(request.user, "role", None) != "landlord" or app.property.landlord_id != request.user.id:
        messages.error(request, "Only the property's landlord can update this application.")
        return redirect('property_detail', pk=app.property_id)

    new_status = request.POST.get("status")
    if new_status not in {"pending", "approved", "rejected"}:
        messages.error(request, "Invalid status.")
        return redirect('property_detail', pk=app.property_id)

    app.status = new_status
    app.save(update_fields=["status"])
    messages.success(request, f"Application status set to {new_status}.")
    return redirect('property_detail', pk=app.property_id)




