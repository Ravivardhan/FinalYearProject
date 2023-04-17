import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
)

cursor=mydb.cursor()
cursor.execute("use cssm")
"""

cursor.execute("insert into users(username,email,password) values('ravi1','ravi1123','ravi1123')")
mydb.commit()


"""




table=cursor.execute("select * from cloud")
files=cursor.fetchall()
print(files)


