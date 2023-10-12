from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.utils import timezone

from .models import *
from .forms import *

# Create your views here.

def current_user(request):
    user = User.objects.filter(email=request.user.email).first()
    return user

def home(request):
    return render(request, "home.html")

def logout_view(request):
    logout(request)
    return render(request, "logout.html")

def geocache_add(request):
    if request.method == 'POST':
        form = GeoCacheForm(request.POST)
        if form.is_valid():
            # Save the question
            latitude, longitude = map(float, form.cleaned_data['location'].split(','))
            geocache = Geocache(name = form.cleaned_data['name'],cacher = current_user(request),cache_date = timezone.now(),lat = latitude, lng = longitude, description = form.cleaned_data['description'],hint = form.cleaned_data['hint'])
            geocache.save()  
            return redirect('home')  
    else:
        form = GeoCacheForm()

    return render(request, 'add.html' , {'form': form} ) 