import json

import pyAesCrypt
from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse,request
# Create your views here.
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
import mysql.connector
from django.template import loader
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage



mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
)

cursor=mydb.cursor()
cursor.execute("use cssm")



def Login(request):
    contex = {}

    if request.method=="POST":
        email=request.POST['email']

        password=request.POST['password']

        print(email,password)

        user=authenticate(username=email,password=password)
        if user is not None:

            cursor.execute(f"select status from users where username='{email}'")
            st=cursor.fetchall()
            status=st[0][0]
            print(status)

            if status==0 or status==None:
                return redirect('verification')
            else:
                login(request, user)
                return redirect('homepage')
        if user is None:
            contex['status']='failed'
    if contex=={}:
        return render(request,'login.html')
    else:

        return render(request,'login.html',context=contex)

def signup(request):
    contex = {}

    if request.method=="POST":
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password2=request.POST.get('confirm_password')

        cursor.execute(f"select * from users where username='{username}'")
        user=cursor.fetchall()
        if user:
            contex['status']='user-already'
            return render(request, 'signup.html', context=contex)
        cursor.execute(f"select * from users where email='{email}'")
        user = cursor.fetchall()
        if user:
            contex['status'] = 'email-already'
            return render(request, 'signup.html', context=contex)


        if password==password2:
            if len(password)<6:
                contex['status'] = 'password-length'
                return render(request, 'signup.html', context=contex)

            usernew=User.objects.create_user(username=username,email=email,password=password)
            usernew.save()
            cursor.execute(f"INSERT INTO users(username,email,password,status) values('{username}','{email}','{password}',0)")
            cursor.execute(f"insert into received(username,received_files) values('{username}','None')")
            mydb.commit()
            return redirect("login")
        #print(username,password,password2)
        else:
            contex['status']='password-match'



    return render(request,'signup.html',context=contex)
def homepage(request):

    if not request.user.is_authenticated:
        return redirect("login")
    username=request.user.get_username()
    cursor.execute(f"select * from requests where username='{username}'")
    requests=cursor.fetchall()
    print(len(requests))
    requests={'requests':len(requests)}
    return render(request,'homepage.html',context=requests)

def Logout(request):
    logout(request)
    return redirect('login')
import mysql.connector
import base64
from PIL import Image
import io
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
        file = request.FILES.get('file_document')
        uploaded_file = file
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        print(fs.url(name))
        type=fs.url(name).split('.')
        type=type[1]
        print(type)
        cursor.execute(f"insert into cloud(file_name,type,file_description,owner,file_key,status) values('{file_name}','{type}','{file_description}','{current_user[0][0]}','{file_key}',0)")
        mydb.commit()

        #       FILE UPLOADING FUNCTIONS

        bufferSize = 64 * 1024
        cursor.execute(f"select file_id from cloud where file_name='{file_name}'")
        file_id = cursor.fetchall()[0][0]

        print(file_id)
        with default_storage.open(uploaded_file.name) as file:
            """ binaryData = file.read()
            #print(binaryData)
            query = f"insert into encrypted_files(file_id,file_content) values(%s,AES_ENCRYPT(%s,'12345'))"

            values = (file_id,str(binaryData))
            cursor.execute(query, values)
            mydb.commit()

            print(file)"""

            """ ###################         AES    ENCRYPTION         ############################"""

            pyAesCrypt.encryptFile(f"media/{file_name}"+"."+f"{fs.url(name).split('.')[-1]}", "data.txt.aes", file_key)
            # decrypt

            f = open("data.txt.aes", "rb")
            encrypted = f.read()

            encrypted = base64.b64encode(encrypted)

            in_query = "INSERT INTO encrypted_files(file_id,file_content) values(%s, %s)"
            cursor.execute(in_query, (file_id, encrypted))

            mydb.commit()

            print("encrypted data inserted into the database successfully")












    return render(request,'upload.html')
def verification(request):
    return render(request,'verification.html')

def cloud(request):
    template = loader.get_template('table.html')

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
        dc['file_type']=i[-1]


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
    #print(cursor.fetchall())


    files_received=cursor.fetchall()
    if files_received != [] or files_received is not None:

        files_received=files_received[0][0].split(',')


        f_r=[]
        for i in files_received:
            print(i)
            if i !='None':
             f_r.append(int(i))
        #print(f_r)
        context['files_received']=f_r

    cursor.execute(f"select * from cloud where owner='{userid}'")
    owned=cursor.fetchall()
    owned_files=[]
    if owned!=[]:
        #print(owned)
        for i in range(len(owned)):
            owned_files.append(owned[i][0])
    #print(owned_files)
    context['owned_files']=owned_files



    requested_file=request.POST.get('collect','')
    #print(requested_file)



    if requested_file:
        requested_file=requested_file.split('-')
        requested_file_name=requested_file[0]
        requested_file_description=requested_file[1]
        requested_file_owner=requested_file[2]
        #print(requested_file_name)

        cursor.execute(f"select file_id from cloud where file_name='{requested_file_name}'")


        file_id=cursor.fetchall()[0][0]
        #print(file_id)

        username = request.user.get_username()



        cursor.execute(f"insert into requests(username,requested_by,file_id) values('{requested_file_owner}','{username}','{file_id}')")
        mydb.commit()
        print("request sent successfully")

    return HttpResponse(template.render(context,request))
def requests(request):
    template = loader.get_template('requests.html')
    username=request.user.get_username()

    cursor.execute(f"select * from requests where username='{username}'")
    files = cursor.fetchall()
    data = {}
    dc = {}
    # print(files)
    for i in files:
        # print(i)

        cursor.execute(f"select file_name from cloud where file_id='{i[2]}'")
        file_name=cursor.fetchall()[0][0]

        dc['file_name']=file_name
        dc['file_id'] = i[2]
        dc['requested_by'] = i[1]
        dc['request_time'] = i[3]

        # print(i[0])
        # print(dc)
        data[i[4]] = dc
        dc = {}

        # print("\n")
        # print(data)

    # print(dc)
    # print(data)

    context = {
        'data': data,
        'table_name': 'REQUESTS'
    }

    requested_file = request.POST.get('collect', '')
    print(requested_file)

    if requested_file:
        requested_file = requested_file.split('-')
        print(requested_file)

        request_file_id=requested_file[0]
        request_file_name=requested_file[1]
        requested_by=requested_file[2]
        request_time=requested_file[3]

        #print(request_file_id,request_file_name,requested_by,request_time)
        username=request.user.get_username()
        cursor.execute(f"select received_files from received where username='{requested_by}'")
        receivd_files=cursor.fetchall()
        print(receivd_files)
        if receivd_files != []:
            received_files_str=str(receivd_files[0][0])+','+str(request_file_id)
            print(received_files_str)
            cursor.execute(f"update received set received_files='{received_files_str}' where username='{requested_by}'")
            mydb.commit()

            #cursor.execute(f"select file_id from cloud where file_name='{requested_file_name}'")
            #file_id = cursor.fetchall()[0][0]
            #username = request.user.get_username()

            #cursor.execute(f"insert into requests(username,requested_by,file_id) values('{requested_file_owner}','{username}','{file_id}')")
            #mydb.commit()
            #print("request sent successfully")


        else:
            print(request_file_id)

            username=request.user.get_username()

            cursor.execute(f"update received set received_files='{request_file_id}' where username='{requested_by}'")
            mydb.commit()
            print("first received file")
        cursor.execute(f"delete from requests where username='{username}' and file_id='{request_file_id}' and requested_by='{requested_by}'")
        mydb.commit()
    return HttpResponse(template.render(context, request))

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
        #print(i[0])
        cursor.execute(f"select username from users where UserID={i[4]}")
        username = cursor.fetchall()
        dc['file_id']=i[0]
        dc['file_name'] = i[1]
        dc['file_description'] = i[2]
        dc['upload_time'] = i[3]
        dc['file_type']=i[-1]

        dc['owner'] = username[0][0]
        # print(i[0])
        # print(dc)
        data[i[0]] = dc


        dc = {}

        # print("\n")
        # print(data)

    # print(dc)
    # print(data)
    print(data)

    context = {
        'data': data,
        'table_name':'MY FILES'
    }

    requested_file = request.POST.get('collect', '')

    if requested_file:
        file=requested_file.split('-')

        def write_file(data, filename):
            # Convert binary data to proper format and write it on Hard Disk
            with open(filename, 'wb') as file:
                file.write(data)
        print(file[-1])

        """query=f"select aes_decrypt(file_content,'12345') from encrypted_files where file_id={file[-1]}"


        cursor.execute(query)



        a = cursor.fetchall()[0][0]
        print(file)"""
        ###################         AES    DECRYPTION         ############################

        cursor.execute(f"select file_content from encrypted_files where file_id='{file[-1]}'")
        content = cursor.fetchall()[0][0]
        print(content)

        decoded_data = base64.b64decode(content)

        f = open("demofile2.txt.aes", "wb")
        f.write(decoded_data)
        f.close()

        pyAesCrypt.decryptFile("demofile2.txt.aes", "dataout2.txt", 'password')

        type = file[1]

        ct = {}
        ct['type'] = type
        print(type)

        data_file = open('dataout2.txt', 'r')
        file_text = data_file.read()

        context={"content":file_text}
        return render(request,"text_file.html",context=context)

        #if type == 'jpg':
           # write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.jpg")
          #  # ct={'url':"C:\Users\Gnaneswar\Desktop\Project\documents\document.jpg"}
         #   return redirect('document')
        #elif type == 'txt':
          #  write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.txt")
         #   return redirect('text_file')
        #elif type == 'mp4':
            #write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.mp4")
           # return redirect('video_file')
       # elif type == 'mp3':
           # write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.mp3")
          #  return redirect('audio_file')





    return HttpResponse(template.render(context, request))



def document(request):
    return render(request,'image_files.html')
def audio_file(request):
    return render(request,'audio_file.html')
def video_file(request):
    return render(request,'video_files.html')
def text_file(request):
    f = open('media/document.txt', 'r')
    file_content = f.read()
    f.close()
    return HttpResponse(file_content, content_type="text/plain")
def received_files(request):
    context = {
        'table_name': 'RECEIVED FILES'
    }
    template = loader.get_template('table.html')
    username=request.user.username
    print(username)

    cursor.execute(f"select * from received where username='{username}'")

    files_received=cursor.fetchall()

    #print(files_received[0][1])
    print(files_received)
    if files_received !=[]:
        if files_received[0][1]==None:
            received_list=''
            list_received=[]
        else:
            received_list = files_received[0][1].split(',')
            list_received = []
            for i in received_list:
                if i != 'None':
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
            dc['file_type']=i[-1]
            dc['file_description'] = i[2]
            dc['upload_time'] = i[3]
            dc['file_id']=i[0]

            dc['owner'] = username[0][0]
            # print(i[0])
            # print(dc)
            data[i[0]] = dc
            dc = {}

        # print(data)
        context['data']=data

    # print(dc)
    # print(data)
    requested_file = request.POST.get('collect', '')

    if requested_file:
        file = requested_file.split('-')
        print(file)

        def write_file(data, filename):
            # Convert binary data to proper format and write it on Hard Disk
            with open(filename, 'wb') as file:
                file.write(data)

        query = f"select aes_decrypt(file_content,'12345') from encrypted_files where file_id={file[-1]}"

        cursor.execute(query)

        a = cursor.fetchall()[0][0]
        print(file)
        type = file[1]

        ct = {}
        ct['type'] = type
        print(type)

        if type == 'jpg':
            write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.jpg")
            # ct={'url':"C:\Users\Gnaneswar\Desktop\Project\documents\document.jpg"}
            return redirect('document')
        elif type == 'txt':
            write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.txt")
            return redirect('text_file')
        elif type == 'mp4':
            write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.mp4")
            return redirect('video_file')
        elif type == 'mp3':
            write_file(a, r"C:\Users\Gnaneswar\Desktop\Project\media\document.mp3")
            return redirect('audio_file')



    return HttpResponse(template.render(context, request))

