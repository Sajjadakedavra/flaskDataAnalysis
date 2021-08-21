import re
from database import MyDatabase
from flask import Flask, render_template, request,url_for,redirect,session,flash
from collections import Counter
# from chatbot import chatbot
import uuid
from flask_mysqldb import MySQL

import json
 
app = Flask(__name__)


app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pb42'
app.config['MYSQL_DB'] = 'flaskdb'
 
mysql = MySQL(app)
 
 


@app.route("/", methods=["POST","GET"])
def consent():
    if 'loggedin' in session:
        return redirect(url_for('index'))
    messages=''
    if request.args:
        messages = json.loads(request.args['messages'])
    #print(messages['msg'])
    return render_template("formm.html", messages=messages)

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        Username = request.form['name']
        mailid = request.form['email']
        accept = request.form['accept']
        cursor = mysql.connection.cursor()
        msg=''
        #cursor.execute(''' INSERT INTO users (Username) VALUES(%s)''',(Username,))

        cursor.execute('SELECT * FROM addresses WHERE email = %s', (mailid,))
        account = cursor.fetchone()
        
        if account:
            cursor.execute('SELECT username FROM addresses WHERE id = %s', (account[0],)) #username is foreign key of users table
            account = cursor.fetchone() #this will only have one element and that is id of users table

            #if both username and id match - this if else and sql statment was added tonight. 
            cursor.execute('SELECT Username from users WHERE id = %s', (account[0],))
            userFromDatabase = cursor.fetchone()
            if userFromDatabase[0] == Username: 
                print('welcome back!')
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[0] #setting session id as id colomn from users table
                #session['username'] = account[1]
                print('session created with id: ', session['id'])
            else:
                messages = json.dumps({"msg":"Invalid Credentials"})
             
                return redirect(url_for('consent', messages=messages))
            
        else:
            print('account created!')
            cursor.execute(''' INSERT INTO users (Username) VALUES(%s)''',(Username,))
            cursor.execute('SELECT * FROM users WHERE username = %s ORDER BY id DESC LIMIT 1', (Username,)) #fetches latest created record even if 2 records are same
            account = cursor.fetchone()
            cursor.execute('INSERT INTO addresses (username, email, accept) VALUES (%s, %s, %s)', (account[0], mailid, accept,))
            session['loggedin'] = True
            session['id'] = account[0]
            #session['username'] = account[1]
            print('session created with id: ', session['id'])

        print("acc details are: ", account)

        mysql.connection.commit()
        cursor.close()
        #return f"Done!!"
        return render_template('index.html')



@app.route("/index", methods=["POST","GET"])
def index():
    if 'loggedin' in session:
        return render_template("index.html")
    
    return redirect(url_for('consent'))     #redirects to homepage if not logged in

@app.route("/chat", methods=["POST","GET"])
def chat():
    return render_template("chatbot.html")

# @app.route("/get")
# def get_bot_response():
#     userText = request.args.get('msg')
#     return str(chatbot.get_response(userText))



@app.route("/res",methods=["POST","GET"])
def res():
    if request.method == 'POST':
        userId = session['id']
        cursor = mysql.connection.cursor()
        # cursor.execute('SELECT username FROM addresses WHERE id = (%s)', (userId,))
        # frKeyId = cursor.fetchone()
        # print("foreing key id is --------> ", frKeyId)
        cursor.execute('SELECT answers FROM users WHERE id = (%s)', (userId,))
        records = cursor.fetchone() #fetch from db

        result=[]
        for rec in records:
            if rec != None:
                originalList = tupleToListToOriginalForm(records) #convert back into original form
                result = originalList #assiging to result, the values fetched from database

        mysql.connection.commit()
        cursor.close()
        
    return render_template("quiz.html", result=result, id = userId)
    if request.method == 'POST' :
        resul=request.form.getlist('info')
        e=resul[0]
        em=e.lower()
        with open("static/abc.txt","w") as file:
            file.write(em)
       

# @app.route("/result",methods=["POST","GET"])
# def result():
#     if request.method == 'POST' :
#         with open("static/abc.txt","r") as file:
#             em=file.read()
        
#         result=request.form.getlist('mycheckbox')
#         if len(result)==25 :
#             counts=Counter(result)
#             if counts['no'] < 9 or counts['no'] == 9:
#                 risk="low"
#                 print("The random id using uuid1() is:",end="")
#                 print(uuid.uuid1())
#                 per=(counts['no']*4)
#                 return render_template("low.html",per=per)
                
#             elif counts['no'] > 9 and counts['no'] < 18 :
#                 risk="moderate"
#                 print("The random id using uuid1() is:",end="")
#                 print(uuid.uuid1())
#                 per=(counts['no']*4)
#                 return render_template("moderate.html",per=per)
                
#             elif counts['no'] > 18 or counts['no'] == 25:
#                 risk="high"
#                 print("The random id using uuid1() is:",end="")
#                 print(uuid.uuid1())
#                 per=(counts['no']*4)
#                 return render_template("high.html",per=per)
#             else :
#                 return render_template("success.html")
#         else :
#             return render_template("err.html")



def listToString(s):
    for num, name in enumerate(s, start=1):
        if name =='':
            s.insert(num, 'undefined')    
    str1 = " " 
    return (str1.join(s)) 



def tupleToList(s):
    for x in s:
        newList = x.split()
    #below commented code will remove the words 'undefined' and get back the original string
    #ogList = []
    #for num, name in enumerate(newList, start=1):
        #if name =='undefined':
            #ogList.insert(num, '') 
        #else:
            #ogList.insert(num, name)

    #return ogList
    return newList

def tupleToListToOriginalForm(s):
    for x in s:
        newList = x.split()
    #below commented code will remove the words 'undefined' and get back the original string
    ogList = []
    for num, name in enumerate(newList, start=1):
        if name =='undefined':
            ogList.insert(num, '') 
        else:
            ogList.insert(num, name)

    return ogList
    #return newList



@app.route("/result",methods=["POST","GET"])
def result():
    if request.method == 'POST':
        result=request.form.getlist('mycheckbox')
        print('original result ==== ', result,'\n')
        conversion = listToString(result)
        print("list to string ===== ", conversion,'\n')
        
        userId = session['id']
        cursor = mysql.connection.cursor()

        # cursor.execute('SELECT username FROM addresses WHERE id = (%s)', (userId,))
        # frKeyId = cursor.fetchone()
        # print("foreing key id is --------> ", frKeyId)
        cursor.execute('UPDATE users SET answers = (%s) WHERE id = (%s)', (conversion, userId,))
        
        cursor.execute('SELECT answers FROM users WHERE id = (%s)', (userId,))
        records = cursor.fetchone() #fetch from db
        print('db result -----> ', records,'\n')
        originalList = tupleToList(records) #convert back into original form
        print('records are -----> ', originalList,'\n')
        mysql.connection.commit()
        cursor.close()


        with open("static/abc.txt","r") as file:
            em=file.read()
        
        result=request.form.getlist('mycheckbox')
        #result = originalList #assiging to result, the values fetched from database
        if len(result)==25 :
            counts=Counter(result)
            if counts['no'] < 9 or counts['no'] == 9:
                risk="low"
                print("The random id using uuid1() is:",end="")
                print(uuid.uuid1())
                per=(counts['no']*4)
                return render_template("low.html",per=per)
                
            elif counts['no'] > 9 and counts['no'] < 18 :
                risk="moderate"
                print("The random id using uuid1() is:",end="")
                print(uuid.uuid1())
                per=(counts['no']*4)
                return render_template("moderate.html",per=per)
                
            elif counts['no'] > 18 or counts['no'] == 25:
                risk="high"
                print("The random id using uuid1() is:",end="")
                print(uuid.uuid1())
                per=(counts['no']*4)
                return render_template("high.html",per=per)
            else :
                return render_template("success.html")
        else :
            return render_template("err.html")

   




# http://localhost:5000/dataAnalysis
@app.route('/dataAnalysis',methods=["POST","GET"])
def dataAnalysis():

    newList = []
    i=0
    yesCount = noCount = 0
    empty = 0
    arrIndex = None

    if request.method == 'POST':
        result=request.form.getlist('number')
        #print('result obtained is: ', result)
        arrIndex = result
   
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT answers FROM users WHERE answers IS NOT NULL')
        records = cursor.fetchall() #fetch from db
        mysql.connection.commit()
        cursor.close()
        for element in records:
            print("element is ",element)
            newList.insert(i, tupleToList(element))
            i=i+1
        for el in newList:
            if el[int(arrIndex[0]) - 1] == 'yes':
                yesCount = yesCount + 1
            elif el[int(arrIndex[0]) - 1] == 'no':
                noCount = noCount + 1
            elif el[int(arrIndex[0]) - 1] == 'undefined':
                empty = empty + 1
        
        #print("YES count is: ", yesCount)
        #print("NO count is ", noCount)
        
    return render_template("checking.html", yesCount=yesCount, noCount=noCount, empty=empty, arrIndex=arrIndex)  




# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('consent'))  #redirects to home page on logout


if __name__ == "__main__":
    
    ob = MyDatabase('mysql', 'root', 'pb42', 'flaskdb')
    ob.create_db_tables()
    print('running...')
    app.run(debug=True)
    


