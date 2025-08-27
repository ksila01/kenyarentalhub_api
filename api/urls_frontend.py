from django.urls import path
from . import views_frontend as views

urlpatterns = [
    path("", views.property_list, name="property_list"),
    path("property/<int:pk>/", views.property_detail, name="property_detail"),
    path("property/new/", views.property_create, name="property_create"),
    path("property/<int:pk>/apply/", views.application_create, name="application_create"),
    path("register/", views.register, name="register"),
]
