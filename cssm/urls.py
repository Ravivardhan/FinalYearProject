from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
urlpatterns = [
    path('', views.Login,name="login"),
    path('logout', views.Logout, name="logout"),

    path('signup/',views.signup,name="signup"),
    path('homepage/',views.homepage,name='homepage')
]
