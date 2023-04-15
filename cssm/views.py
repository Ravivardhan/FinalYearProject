from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse,request
# Create your views here.
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User

def Login(request):
    if request.method=="POST":
        email=request.POST['email']

        password=request.POST['password']

        user=authenticate(username=email,password=password)
        if user is not None:
            login(request,user)
            return redirect("homepage")


    return render(request,'login.html')

def signup(request):

    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password2=request.POST.get('confirm_password')
        if password==password2:
            usernew=User.objects.create_user(username=username,email=email,password=password)
            usernew.save()
            return redirect("homepage")
        #print(username,password,password2)

    return render(request,'signup.html')
def homepage(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request,'homepage.html')

def Logout(request):
    logout(request)
    return redirect('login')