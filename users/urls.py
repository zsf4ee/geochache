from django.urls import path
from . import views

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("logout", views.logout_view, name="logout"),
    path("login", views.login_view, name="login"),
    path("add", views.geocache_add, name="add"),
    path("catalog", views.catalog, name="catalog"),
    path("bounds", views.geocaches_within_bounds, name="bounds"),
    path("cache", views.cache, name="cache"),
    path("approval", views.approve, name="approve"),
    path("checkoff/<int:pk>/", views.checkoff, name="checkoff"),
    path("decline/<int:pk>/", views.decline, name="decline"),
    path("find/<int:pk>/", views.find, name="find"),
    path("search/<str:role>/<str:text>", views.search, name="search"),
    path("pending", views.pending, name="pending"),
    path("leaderboard/<int:top>",views.leaderboard,name="leaderboard"),
    path("profile/<int:pk>",views.profile,name="profile")
]
