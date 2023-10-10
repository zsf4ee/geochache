from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('logout', views.logout_view, name = "logout"),
    path('add', views.geocache_add, name = "add")
]
