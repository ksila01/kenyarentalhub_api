from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Property, RentalApplication, Payment

User = get_user_model()

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ["name", "category", "description", "location", "price", "is_available", "image"]

class RentalApplicationForm(forms.ModelForm):
    class Meta:
        model = RentalApplication
        fields = ["property", "message"]

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "password1", "password2"]
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount"]