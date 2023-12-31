from datetime import timedelta
from django.http import HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages


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
                password=form.cleaned_data["password"],
                radius=form.cleaned_data["radius"],
            )
            geocache.save()

            # TODO: Create hint here

            return redirect("hint/" + str(geocache.pk))
        else:
            print(form.errors)

    else:
        form = GeoCacheForm()

    return render(request, "add.html", {"form": form})


@login_required
def hint(request, pk):
    geocache = get_object_or_404(Geocache, pk=pk)
    if request.method == "POST":
        form = HintForm(request.POST)
        if form.is_valid():
            # Save the question
            hint = Hint(
                text=form.cleaned_data["text"],
                geocache=geocache,
                number=Hint.objects.filter(geocache=geocache).count() + 1,
            )
            hint.save()

            if Hint.objects.filter(geocache=geocache).count() == 4:
                cache_url = reverse("cache") + f"?lat={geocache.lat}&lng={geocache.lng}"
                return HttpResponseRedirect(cache_url)
            return HttpResponseRedirect(reverse("hint", args=[geocache.pk]))
        else:
            print(form.errors)

    else:
        form = HintForm()
    hints = Hint.objects.filter(geocache=geocache)

    return render(
        request, "hint.html", {"form": form, "hints": hints, "geocache": geocache}
    )


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
    hints = [hint.text for hint in Hint.objects.filter(geocache=geocache)]
    print(hints)
    user_has_find = any(request.user == find.finder for find in finds)
    has_password = len(geocache.password) > 0
    has_hints = len(hints) > 0
    
    context = {
        "geocache": geocache,
        "finds": finds,
        "comments": comments,
        "user_has_find": user_has_find,
        "form": form,
        "hints": hints,
        "has_password": has_password,
        "has_hints": has_hints
    }

    return render(request, "cache.html", context)


@login_required
def approve(request):
    if not request.user.is_authenticated:
        messages.error(request, "You do not have the permission to approve caches.")
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


def find_with_password(request, pk, text):
    geocache = get_object_or_404(Geocache, pk=pk)
    if text == geocache.password:
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
        messages.success(request, "Find logged!")
    else:
        messages.error(request, "The password does not match. Please try again.")
    cache_url = reverse("cache") + f"?lat={geocache.lat}&lng={geocache.lng}"
    return HttpResponseRedirect(cache_url)

def find_without_password(request, pk):
    geocache = get_object_or_404(Geocache, pk=pk)
    
    if len(geocache.password) == 0:
        print("gewrasdfa")
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
        messages.success(request, "Find Registered!!")
    else:
        messages.error(request, "Please enter the correct password to log your find.")
        
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
def leaderboard(request):
    users = User.objects.filter().order_by("-find_count")
    return render(request, "leaderboard.html", {"users": users})


@login_required
def profile(request, pk):
    profile = get_object_or_404(User, pk=pk)
    geocaches = Geocache.objects.filter(active=True, cacher=profile)
    finds = Find.objects.filter(finder=profile)
    return render(request, "profile.html", {"profile": profile, "geocaches": geocaches, "finds": finds})


@login_required
def confirm_delete(request, pk):
    geocache = Geocache.objects.filter(pk=pk).first()
    return render(request, "confirm_delete.html", {"pk": pk, "lat": geocache.lat, "lng": geocache.lng})

@login_required
def delete(request, pk):
    geocache = Geocache.objects.filter(pk=pk).first()
    
    if request.user == geocache.cacher or request.user.is_admin:
        geocache.delete()
        messages.success(request, "Cache deleted.")
        return redirect("catalog")
    else: 
        cache_url = reverse("cache") + f"?lat={geocache.lat}&lng={geocache.lng}"
        messages.error(request, "You do not have the permission to delete that cache.")
        return HttpResponseRedirect(cache_url)




