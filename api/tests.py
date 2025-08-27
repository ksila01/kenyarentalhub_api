from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Property

User = get_user_model()

class PropertyModelTest(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(username="land1", password="testpass", role="landlord")
        self.property = Property.objects.create(
            landlord=self.landlord,
            name="Test Apartment",
            category="apartment",
            location="Nairobi",
            price=50000
        )

    def test_property_str(self):
        self.assertEqual(str(self.property), "Test Apartment - Nairobi")

class ViewTest(TestCase):
    def test_home_page_status(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
