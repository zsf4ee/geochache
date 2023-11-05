from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('logout', views.logout_view, name = "logout"),
    path('add', views.geocache_add, name = "add"),
    path('catalog', views.catalog, name = "catalog"),
    path('bounds', views.geocaches_within_bounds, name="bounds"),
    path('cache',views.cache, name="cache"),
    path('approval',views.approve, name="approve"),
    path('checkoff/<int:pk>/',views.checkoff,name="checkoff"),
]
