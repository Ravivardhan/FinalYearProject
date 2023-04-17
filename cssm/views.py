from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse,request
# Create your views here.
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
import mysql.connector
from django.template import loader


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
)

cursor=mydb.cursor()
cursor.execute("use cssm")



def Login(request):
    if request.method=="POST":
        email=request.POST['email']

        password=request.POST['password']

        user=authenticate(username=email,password=password)
        if user is not None:

            cursor.execute(f"select status from users where username='{email}'")
            st=cursor.fetchall()
            status=st[0][0]
            print(status)

            if status==0:
                return redirect('verification')
            else:
                login(request, user)
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
            cursor.execute(f"INSERT INTO users(username,email,password,status) values('{username}','{email}','{password}',0)")
            cursor.execute(f"insert into received(username) values('{username}')")
            mydb.commit()
            return redirect("login")
        #print(username,password,password2)

    return render(request,'signup.html')
def homepage(request):
    if not request.user.is_authenticated:
        return redirect("login")
    requests={'requests':1}
    return render(request,'homepage.html',context=requests)

def Logout(request):
    logout(request)
    return redirect('login')

def upload(request):
    if request.method=="POST":
        file_name=request.POST.get('file_name')
        file_description=request.POST.get('file_description')
        file_key=request.POST.get('file_key')


        print(file_name,file_description,file_key)
        username=request.user.get_username()
        cursor.execute(f"select UserID from users where username='{username}'")
        current_user=cursor.fetchall()
        print(current_user[0][0])
        cursor.execute(f"insert into cloud(file_name,file_description,owner,file_key) values('{file_name}','{file_description}','{current_user[0][0]}','{file_key}')")
        mydb.commit()
    return render(request,'upload.html')
def verification(request):
    return render(request,'verification.html')

def cloud(request):
    template = loader.get_template('table.html')

    cursor.execute("select * from cloud")
    files = cursor.fetchall()
    data={}
    dc={}
    #print(files)
    for i in files:
        #print(i)
        cursor.execute(f"select username from users where UserID={i[4]}")
        username = cursor.fetchall()


        dc['file_name']=i[1]
        dc['file_description']=i[2]
        dc['upload_time']=i[3]


        dc['owner']=username[0][0]
        #print(i[0])
        #print(dc)
        data[i[0]]=dc
        dc={}

        #print("\n")
        #print(data)

    #print(dc)
    #print(data)


    context = {
        'data': data,
        'table_name': 'CLOUD'
    }





    return HttpResponse(template.render(context,request))

def myfiles(request):
    template = loader.get_template('table.html')
    username=request.user.get_username()
    cursor.execute(f"select UserID from users where username='{username}'")
    id=cursor.fetchall()
    cursor.execute(f"select * from cloud where owner='{id[0][0]}'")
    files = cursor.fetchall()
    print(files)
    data = {}
    dc = {}
    # print(files)
    for i in files:
        # print(i)
        cursor.execute(f"select username from users where UserID={i[4]}")
        username = cursor.fetchall()

        dc['file_name'] = i[1]
        dc['file_description'] = i[2]
        dc['upload_time'] = i[3]

        dc['owner'] = username[0][0]
        # print(i[0])
        # print(dc)
        data[i[0]] = dc
        dc = {}

        # print("\n")
        # print(data)

    # print(dc)
    # print(data)

    context = {
        'data': data,
        'table_name':'MY FILES'
    }

    return HttpResponse(template.render(context, request))




def received_files(request):
    template = loader.get_template('table.html')
    username=request.user.get_username()

    cursor.execute(f"select * from received where username='{username}'")

    files_received=cursor.fetchall()

    #print(files_received[0][1])
    received_list=files_received[0][1].split(',')
    list_received=[]
    for i in received_list:
        list_received.append(int(i))

    #print(list_received)
    files=[]
    for i in list_received:
        cursor.execute(f"select * from cloud where file_id='{i}'")
        file=cursor.fetchall()
        files.append(file[0])

    print(files)
    data = {}
    dc = {}
    # print(files)
    for i in files:
        # print(i)
        cursor.execute(f"select username from users where UserID={i[4]}")
        username = cursor.fetchall()

        dc['file_name'] = i[1]
        dc['file_description'] = i[2]
        dc['upload_time'] = i[3]

        dc['owner'] = username[0][0]
        # print(i[0])
        # print(dc)
        data[i[0]] = dc
        dc = {}

        # print(data)

    # print(dc)
    # print(data)

    context = {
        'data': data,
        'table_name':'RECEIVED FILES'
    }


    return HttpResponse(template.render(context, request))

