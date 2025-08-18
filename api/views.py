from django.shortcuts import render
from rest_framework import viewsets
from .models import RentalProperty
from .serializers import RentalPropertySerializer

class RentalPropertyViewSet(viewsets.ModelViewSet):
    queryset = RentalProperty.objects.all()
    serializer_class = RentalPropertySerializer
