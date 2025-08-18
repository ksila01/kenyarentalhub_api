from rest_framework import serializers
from .models import RentalProperty
from django.contrib.auth import get_user_model
from .models import RentalProperty, RentalApplication

class RentalPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalProperty
        fields = '__all__'


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


class RentalPropertySerializer(serializers.ModelSerializer):
    landlord = UserSerializer(read_only=True)

    class Meta:
        model = RentalProperty
        fields = ['id', 'name', 'category', 'description', 'location', 'price', 'available', 'landlord', 'created_at']


class RentalApplicationSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    rental_property = RentalPropertySerializer(read_only=True)

    class Meta:
        model = RentalApplication
        fields = ['id', 'tenant', 'rental_property', 'message', 'status', 'applied_at']
