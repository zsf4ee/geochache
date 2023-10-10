from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.utils import timezone

from .models import *
from .forms import *

# Create your views here.

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
            geocache = Geocache(name = form.cleaned_data['name'],cache_date = timezone.now, description = form.cleaned_data['description'],hint = form.cleaned_data['hint'])
            geocache.save()  
            return redirect('home')  
    else:
        form = GeoCacheForm()

    return render(request, 'add.html' , {'form':form} ) 