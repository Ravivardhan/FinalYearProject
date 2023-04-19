from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('', views.Login,name="login"),
    path('logout', views.Logout, name="logout"),
    path('verification', views.verification, name="verification"),
    path('homepage/cloud', views.cloud, name="cloud"),
    path('homepage/upload',views.upload,name='upload'),
    path('signup/',views.signup,name="signup"),
    path('homepage/',views.homepage,name='homepage'),
    path('homepage/myfiles',views.myfiles,name='myfiles'),
    path('homepage/receivedfiles', views.received_files, name='receivedfiles'),
    path('homepage/requests',views.requests,name='requests'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

