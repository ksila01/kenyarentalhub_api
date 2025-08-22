# api/serializers.py
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers

from .models import Property, RentalApplication

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "password"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        # Validate password with Django’s validators
        password = attrs.get("password")
        user = User(**{k: v for k, v in attrs.items() if k != "password"})
        try:
            validate_password(password, user=user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        # Validate role
        if attrs.get("role") not in ("tenant", "landlord"):
            raise serializers.ValidationError({"role": "Role must be 'tenant' or 'landlord'."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PropertySerializer(serializers.ModelSerializer):
    landlord = serializers.ReadOnlyField(source="landlord.username")

    class Meta:
        model = Property
        fields = [
            "id", "landlord", "name", "category", "description",
            "location", "price", "is_available", "created_at"
        ]
        read_only_fields = ["id", "landlord", "created_at"]


class RentalApplicationSerializer(serializers.ModelSerializer):
    tenant = serializers.ReadOnlyField(source="tenant.username")
    property_name = serializers.ReadOnlyField(source="property.name")

    class Meta:
        model = RentalApplication
        fields = ["id", "property", "property_name", "tenant", "message", "status", "created_at"]
        read_only_fields = ["id", "tenant", "status", "created_at", "property_name"]

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        prop = attrs.get("property")

        # Only tenants can create applications
        if not user.is_authenticated or user.role != "tenant":
            raise serializers.ValidationError("Only tenants can apply for a property.")

        # Cannot apply to your own property
        if prop and prop.landlord_id == user.id:
            raise serializers.ValidationError("You cannot apply to your own property.")

        # Property must be available
        if prop and not prop.is_available:
            raise serializers.ValidationError("This property is not available.")

        return attrs

    def create(self, validated_data):
        validated_data["tenant"] = self.context["request"].user
        # Unique-together (property, tenant) will also guard duplicates
        return super().create(validated_data)

