from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.db import IntegrityError
from rest_framework import serializers

from .models import Property, RentalApplication, Payment, Review

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "password"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        password = attrs.get("password")
        user = User(**{k: v for k, v in attrs.items() if k != "password"})
        try:
            validate_password(password, user=user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
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
            "location", "price", "is_available", "created_at", "image"
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

        if not user.is_authenticated or user.role != "tenant":
            raise serializers.ValidationError("Only tenants can apply for a property.")
        if prop and prop.landlord_id == user.id:
            raise serializers.ValidationError("You cannot apply to your own property.")
        if prop and not prop.is_available:
            raise serializers.ValidationError("This property is not available.")
        return attrs

    def create(self, validated_data):
        validated_data["tenant"] = self.context["request"].user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError("You have already applied for this property.")


class PaymentSerializer(serializers.ModelSerializer):
    tenant = serializers.ReadOnlyField(source="application.tenant.username")
    property_name = serializers.ReadOnlyField(source="application.property.name")

    class Meta:
        model = Payment
        fields = ["id", "application", "tenant", "property_name", "amount", "status", "transaction_id", "created_at"]
        read_only_fields = ["id", "status", "transaction_id", "created_at", "tenant", "property_name"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    tenant = serializers.ReadOnlyField(source="tenant.username")
    property_name = serializers.ReadOnlyField(source="property.name")

    class Meta:
        model = Review
        fields = ["id", "property", "property_name", "tenant", "rating", "comment", "created_at"]
        read_only_fields = ["id", "tenant", "property_name", "created_at"]
