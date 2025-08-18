from rest_framework import serializers
from .models import RentalProperty

class RentalPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalProperty
        fields = '__all__'