from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse,request
# Create your views here.
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
import mysql.connector
from django.template import loader
from django.contrib.auth.models import User


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
        print(email,password)
        if user is not None:

            cursor.execute(f"select * from users where username='{email}'")
            st=cursor.fetchall()
            print(st[0][1],st[0][3])
            if email==st[0][1] and password==st[0][3]:
                login(request,user)
                return redirect("csp_homepage")


    return render(request,'csp_login.html')
def Logout(request):
    logout(request)
    return redirect('login')
def homepage(request):
    cursor.execute("select * from users where status=0")
    requests=cursor.fetchall()
    print(requests)

    cursor.execute("select * from cloud where status=0")
    file_requests = cursor.fetchall()
    print(file_requests)



    requests = {'user_requests': len(requests),
                'file_requests':len(file_requests)}
    return render(request,'csp_homepage.html',context=requests)

def users(request):
    template = loader.get_template('csp_users.html')

    cursor.execute("select * from users")
    files = cursor.fetchall()
    data = {}
    dc = {}
    # print(files)
    for i in files:
        print(i)



        dc['file_name'] = i[1]
        dc['file_description'] = i[2]
        dc['upload_time'] = i[3]
        dc['file_id'] = i[0]
        dc['user_status']=i[-1]

        # print(i[0])
        # print(dc)
        data[i[0]] = dc
        dc = {}

        # print("\n")
        # print(data)

    # print(dc)
    # print(data)
    username = request.user.get_username()
    context = {
        'data': data,
        'table_name': 'CLOUD',
        'current_user': username,
    }

    if request.method=="POST":
        requested_file = request.POST.get('collect', '')
        suspend_username=requested_file.split('-')[1]
        suspend_email=requested_file.split('-')[2]
        cursor.execute(f"update users set status=0 where username='{suspend_username}'")

        mydb.commit()





    return render(request,'csp_users.html',context=context)


def userrequests(request):
    template = loader.get_template('user_requests.html')

    cursor.execute("select * from users where status='0'")
    files = cursor.fetchall()
    data = {}
    dc = {}
    # print(files)
    for i in files:
        print(i)

        dc['file_name'] = i[1]
        dc['file_description'] = i[2]
        dc['upload_time'] = i[3]
        dc['file_id'] = i[0]
        dc['user_status'] = i[-1]

        # print(i[0])
        # print(dc)
        data[i[0]] = dc
        dc = {}

        # print("\n")
        # print(data)

    # print(dc)
    # print(data)
    username = request.user.get_username()
    context = {
        'data': data,
        'table_name': 'USER REQUESTS',
        'current_user': username,
    }

    if request.method == "POST":
        requested_file = request.POST.get('collect', '')
        suspend_username = requested_file.split('-')[1]
        suspend_email = requested_file.split('-')[2]
        cursor.execute(f"update users set status=1  where username='{suspend_username}'")

        mydb.commit()

    return render(request, 'user_requests.html', context=context)


def file_requests(request):
    template = loader.get_template('file_requests.html')

    cursor.execute("select * from cloud where status='0'")
    files = cursor.fetchall()
    data = {}
    dc = {}
    # print(files)
    for i in files:
        print(i)

        cursor.execute(f"select username from users where UserID='{i[4]}'")
        uname=cursor.fetchall()

        dc['file_name'] = i[1]
        dc['file_description'] = i[2]
        dc['upload_time'] = i[3]
        dc['file_id'] = i[0]
        dc['owner']=uname[0][0]
        dc['user_status'] = i[-1]

        # print(i[0])
        # print(dc)
        data[i[0]] = dc
        dc = {}

        # print("\n")
        # print(data)

    # print(dc)
    # print(data)
    username = request.user.get_username()
    context = {
        'data': data,
        'table_name': 'FILE REQUESTS',
        'current_user': username,
    }

    if request.method == "POST":
        requested_file = request.POST.get('collect', '')
        suspend_username = requested_file.split('-')[1]
        suspend_email = requested_file.split('-')[2]
        cursor.execute(f"update cloud set status=1  where file_id='{requested_file.split('-')[0]}'")
        mydb.commit()

    return render(request, 'file_requests.html', context=context)

def cloud(request):
    template = loader.get_template('csp_cloud.html')

    cursor.execute("select * from cloud where status=1")
    files = cursor.fetchall()
    data={}
    dc={}
    #print(files)
    for i in files:
        #print(i)
        cursor.execute(f"select username from users where UserID={i[4]}")
        username = cursor.fetchall()


        dc['file_id']=i[0]
        dc['file_name']=i[1]
        dc['file_description']=i[2]
        dc['upload_time']=i[3]
        dc['file_id']=i[0]


        dc['owner']=username[0][0]
        #print(i[0])
        #print(dc)
        data[i[0]]=dc
        dc={}

        #print("\n")
        #print(data)

    #print(dc)
    #print(data)
    username=request.user.get_username()
    context = {
        'data': data,
        'table_name': 'CLOUD',
        'current_user': username,
    }

    cursor.execute(f"select UserID from users where username='{request.user.get_username()}'")
    userid=cursor.fetchall()[0][0]

    cursor.execute(f"select received_files from received where username='{request.user.get_username()}'")
    print(cursor.fetchall())



    if cursor.fetchall() != []:
        files_received=cursor.fetchall()
        files_received=files_received[0][0].split(',')


        f_r=[]
        for i in files_received:
            f_r.append(int(i))
        print(f_r)
        context['files_received']=f_r

    cursor.execute(f"select * from cloud where owner='{userid}'")
    owned=cursor.fetchall()
    owned_files=[]
    if owned!=[]:
        print(owned)
        for i in range(len(owned)):
            owned_files.append(owned[i][0])
    print(owned_files)
    context['owned_files']=owned_files





    return HttpResponse(template.render(context,request))