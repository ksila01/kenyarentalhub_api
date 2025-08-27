from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# -------- Custom User --------
class User(AbstractUser):
    ROLE_CHOICES = (("tenant", "Tenant"), ("landlord", "Landlord"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


# Optional profile (keep minimal for now)
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)


# -------- Property --------
class Property(models.Model):
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="properties"
    )
    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=100,
        choices=[
            ("apartment", "Apartment"),
            ("house", "House"),
            ("bedsitter", "Bedsitter"),
            ("single_room", "Single Room"),
        ],
    )
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.location}"


# -------- Rental Application --------
class RentalApplication(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="applications")
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    message = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("property", "tenant")

    def __str__(self):
        return f"{self.tenant.username} -> {self.property.name} ({self.status})"
class Payment(models.Model):
    application = models.ForeignKey(
        RentalApplication,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=50,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending"
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"


class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reviews")
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField()  # 1–5 scale
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("property", "tenant")

    def __str__(self):
        return f"Review by {self.tenant.username} on {self.property.name}"
