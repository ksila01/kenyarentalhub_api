from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Property
from .forms import PropertyForm, RentalApplicationForm, UserRegisterForm

def property_list(request):
    properties = Property.objects.filter(is_available=True).order_by("-created_at")
    return render(request, "api/property_list.html", {"properties": properties})

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, "api/property_detail.html", {"property": property})

@login_required
def property_create(request):
    if request.method == "POST":
        form = PropertyForm(request.POST)
        if form.is_valid():
            prop = form.save(commit=False)
            prop.landlord = request.user
            prop.save()
            return redirect("property_list")
    else:
        form = PropertyForm()
    return render(request, "api/property_form.html", {"form": form})

@login_required
def application_create(request, pk):
    if request.method == "POST":
        form = RentalApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.tenant = request.user
            app.save()
            return redirect("property_detail", pk=pk)
    else:
        form = RentalApplicationForm(initial={"property": pk})
    return render(request, "api/application_form.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("property_list")
    else:
        form = UserRegisterForm()
    return render(request, "api/register.html", {"form": form})
