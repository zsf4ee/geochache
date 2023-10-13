from django.http import HttpResponseNotFound, JsonResponse
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
            geocache = Geocache(name = form.cleaned_data['name'],cacher = current_user(request),cache_date = timezone.now(),lat = latitude, lng = longitude, description = form.cleaned_data['description'],hint = form.cleaned_data['hint'],radius = form.cleaned_data['radius'])
            geocache.save()  
            return redirect('catalog')  
        else:
            print(form.errors)

    else:
        form = GeoCacheForm()

    return render(request, 'add.html' , {'form': form} ) 

def catalog(request):
    return render(request, 'catalog.html')

def geocaches_within_bounds(request):
    ne_lat = request.GET.get('ne_lat')
    ne_lng = request.GET.get('ne_lng')
    sw_lat = request.GET.get('sw_lat')
    sw_lng = request.GET.get('sw_lng')

    geocaches = Geocache.objects.filter(
        lat__lte=ne_lat,
        lat__gte=sw_lat,
        lng__lte=ne_lng,
        lng__gte=sw_lng
    ).values('lat', 'lng','radius')

    if(geocaches.exists()):
        return JsonResponse(list(geocaches), safe=False)
    else:
        return HttpResponseNotFound("No geocaches found.")
    
def cache(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')     

    geocache = Geocache.objects.filter(lat=lat,lng=lng).first()
    finds = Find.objects.filter(geocache=geocache).order_by('-timestamp')
    comments = Comment.objects.filter(geocache=geocache).order_by('-date')



    context = {
        'geocache': geocache,
        'finds': finds,
        'comments': comments
    }
    
    return render(request, 'cache.html', context)
    
