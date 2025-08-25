from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Property, RentalApplication
from .serializers import UserSerializer, PropertySerializer, RentalApplicationSerializer
from .permissions import IsLandlord, IsTenant, IsOwnerOrReadOnly

User = get_user_model()

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

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by("-created_at")
    serializer_class = PropertySerializer
    def get_permissions(self):
        #if self.action == "create":
          #  if self.request.user.is_authenticated:
           #     return [IsAuthenticated(), IsTenant()]  # only tenants can POST
           # return [AllowAny()]  # show form in browsable API
        #elif self.action in ["update", "partial_update", "destroy"]:
           # return [IsAuthenticated()]
        #return [IsAuthenticated()]
        return [AllowAny()]


    def perform_create(self, serializer):
        #serializer.save(landlord=self.request.user)
         from django.contrib.auth import get_user_model
         User = get_user_model()
         # Get any existing landlord user
         landlord_user = User.objects.filter(role="landlord").first()
         serializer.save(landlord=landlord_user)

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
    queryset = RentalApplication.objects.select_related("property", "tenant", "property__landlord").all()

    def get_permissions(self):
        #if self.action == "create":
            # if self.request.user.is_authenticated:
               # return [IsAuthenticated(), IsTenant()]  # only tenants can POST
          #  return [AllowAny()]  # show form in browsable API
        #elif self.action in ["update", "partial_update", "destroy"]:
            #return [IsAuthenticated()]
        #return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
       # serializer.save(tenant=self.request.user)
        serializer.save ()

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

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

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

