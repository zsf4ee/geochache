from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login', views.login_view, name = "login"),
    path('add', views.geocache_add, name = "add"),
    path('catalog', views.catalog, name = "catalog"),
    path('bounds', views.geocaches_within_bounds, name="bounds"),
    path('cache',views.cache, name="cache"),
    path('approval',views.approve, name="approve"),
    path('getactive',views.getactive,name="getactive")
]
