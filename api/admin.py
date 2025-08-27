from django.contrib import admin
from .models import User, Profile, Property, RentalApplication, Payment, Review

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff")
    search_fields = ("username", "email")

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "landlord", "price", "is_available", "created_at")
    list_filter = ("is_available", "category")
    search_fields = ("name", "location")

@admin.register(RentalApplication)
class RentalApplicationAdmin(admin.ModelAdmin):
    list_display = ("tenant", "property", "status", "created_at")
    list_filter = ("status",)

admin.site.register(Profile)
admin.site.register(Payment)
admin.site.register(Review)

