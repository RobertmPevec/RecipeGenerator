from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path
from .views import login_register_view 

urlpatterns = [
    path("login/", login_register_view, name="login"),
    path("register/", login_register_view, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_user, name="logout"),
    path("", views.home, name="home"), 
]