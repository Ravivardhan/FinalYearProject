
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



bufferSize = 64 * 1024

with default_storage.open("sample.txt") as file:
    binaryData = file.read()
    # print(binaryData)
    query = f"insert into encrypted_files(file_id,file_content) values(%s,AES_ENCRYPT(%s,'12345'))"

    values = ('100', str(binaryData))
    cursor.execute(query, values)
    mydb.commit()
