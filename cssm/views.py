from django.shortcuts import render
from django.http import HttpRequest,HttpResponse,request
# Create your views here.
from django.contrib.auth import login,authenticate
from django.contrib.auth.models import User

def login(request):
    return render(request,'login.html')

def signup(request):

    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password2=request.POST.get('confirm_password')
        if password==password2:
            usernew=User.objects.create_user(username=username,email=email,password=password)
            return HttpResponse("USER CREATED SUCCESSFULLY")
        #print(username,password,password2)

    return render(request,'signup.html')
def homepage(request):
    return render(request,'homepage.html')