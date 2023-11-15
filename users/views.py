from datetime import timedelta
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q


from .models import *
from .forms import *

# Create your views here.


def welcome(request):
    if request.user.is_authenticated:
        return redirect("catalog")
    return render(request, "welcome.html")


def login_view(request):
    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    return render(request, "welcome.html")

@login_required
def geocache_add(request):
    if request.method == "POST":
        form = GeoCacheForm(request.POST)
        if form.is_valid():
            # Save the question
            latitude, longitude = map(float, form.cleaned_data["location"].split(","))
            geocache = Geocache(
                name=form.cleaned_data["name"],
                cacher=request.user,
                cache_date=timezone.localtime(timezone.now()),
                lat=latitude,
                lng=longitude,
                description=form.cleaned_data["description"],
                hint=form.cleaned_data["hint"],
                radius=form.cleaned_data["radius"],
            )
            geocache.save()
            return redirect("catalog")
        else:
            print(form.errors)

    else:
        form = GeoCacheForm()

    return render(request, "add.html", {"form": form})

@login_required
def catalog(request):
    return render(request, "catalog.html")

@login_required
def geocaches_within_bounds(request):
    ne_lat = request.GET.get("ne_lat")
    ne_lng = request.GET.get("ne_lng")
    sw_lat = request.GET.get("sw_lat")
    sw_lng = request.GET.get("sw_lng")

    geocaches = Geocache.objects.filter(
        lat__lte=ne_lat, lat__gte=sw_lat, lng__lte=ne_lng, lng__gte=sw_lng, active=True
    ).values("lat", "lng", "radius")

    if geocaches.exists():
        return JsonResponse(list(geocaches), safe=False)
    else:
        return HttpResponseNotFound("No geocaches found.")

@login_required
def cache(request):
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    geocache = Geocache.objects.filter(lat=lat, lng=lng).first()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                geocache=geocache,
                user=request.user,
                date=timezone.localtime(timezone.now()),
                text=form.cleaned_data["text"],
            )
            comment.save()

        else:
            print(form.errors)
        cache_url = reverse("cache") + f"?lat={geocache.lat}&lng={geocache.lng}"
        return HttpResponseRedirect(cache_url)

    form = CommentForm()

    finds = Find.objects.filter(geocache=geocache).order_by("-timestamp")
    comments = Comment.objects.filter(geocache=geocache).order_by("-date")
    user_has_find = any(request.user == find.finder for find in finds)

    context = {
        "geocache": geocache,
        "finds": finds,
        "comments": comments,
        "user_has_find": user_has_find,
        "form": form,
    }

    return render(request, "cache.html", context)

@login_required
def approve(request):
    if not request.user.is_authenticated:
        return redirect("catalog")
    else: 
        geocaches = Geocache.objects.filter(active=False)
        return render(request, "approve.html", {"geocaches": geocaches})

@login_required
def search(request, text, role):
    if role == "admin":
        geocaches = Geocache.objects.filter(
            Q(name__istartswith=text)
            | Q(name__icontains=text)
            | Q(name__iendswith=text)
        )
    else:
        geocaches = Geocache.objects.filter(
            Q(name__istartswith=text)
            | Q(name__icontains=text)
            | Q(name__iendswith=text),
            active=True,
        )
    return render(request, "search.html", {"geocaches": geocaches})

@login_required
def checkoff(request, pk):
    geocache = get_object_or_404(Geocache, pk=pk)
    if geocache.declined == True:
        geocache.declined = False
    geocache.active = True
    geocache.admin = request.user
    geocache.admin_date = timezone.localtime(timezone.now())
    geocache.save()
    cache_url = reverse("cache") + f"?lat={geocache.lat}&lng={geocache.lng}"
    return HttpResponseRedirect(cache_url)

@login_required
def decline(request, pk):
    geocache = get_object_or_404(Geocache, pk=pk)
    cache_url = reverse("cache") + f"?lat={geocache.lat}&lng={geocache.lng}"
    if request.method == "POST":
        form = DeclineForm(request.POST)
        if form.is_valid():
            geocache.reason = form.cleaned_data["text"]
            geocache.declined = True
            geocache.active = False
            geocache.admin = request.user
            geocache.admin_date = timezone.localtime(timezone.now())
            geocache.save()
            return HttpResponseRedirect(cache_url)
    form = DeclineForm()
    return render(request, "decline.html", {"geocache": geocache, "form": form})

@login_required
def find(request, pk):
    geocache = get_object_or_404(Geocache, pk=pk)
    find = Find(
        finder=request.user,
        geocache=geocache,
        timestamp=timezone.localtime(timezone.now()),
    )
    find.save()
    request.user.find_count += 1
    request.user.save()
    geocache.find_count += 1
    geocache.save()
    cache_url = reverse("cache") + f"?lat={geocache.lat}&lng={geocache.lng}"
    return HttpResponseRedirect(cache_url)

@login_required
def pending(request):
    geocaches = Geocache.objects.filter(
        Q(active=False) | Q(admin_date__gte=timezone.now() - timedelta(hours=12)),
        cacher=request.user,
    )
    return render(request, "pending.html", {"geocaches": geocaches})

@login_required
def leaderboard(request, top):
    users = User.objects.filter().order_by("-find_count")[:top]
    return render(request, "leaderboard.html", {"users": users})

@login_required
def profile(request, pk):
    profile = get_object_or_404(User, pk=pk)
    geocaches = Geocache.objects.filter(active=True, cacher=profile)
    return render(request, "profile.html", {"profile": profile, "geocaches": geocaches})

