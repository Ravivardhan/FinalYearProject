from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
urlpatterns = [
    path('', views.Login,name="csp_login"),
    path('/homepage', views.homepage, name="csp_homepage"),
    path('/homepage/users', views.users, name="csp_users"),
    path('/homepage/userrequests',views.userrequests,name="user_requests"),
    path('/homepage/filerequests', views.file_requests, name="file_requests"),
    path('/homepage/cspcloud',views.cloud,name='csp_cloud')

]