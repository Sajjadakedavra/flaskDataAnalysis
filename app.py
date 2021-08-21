from flask import Flask, render_template, request,url_for,redirect,session,flash
from collections import Counter
from chatbot import chatbot
import uuid
from flask_mysqldb import MySQL
 
app = Flask(__name__)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)
 
 


@app.route("/", methods=["POST","GET"])
def consent():
    return render_template("formm.html")

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
     
    if request.method == 'POST':
        Username = request.form['name']
        mailid = request.form['email']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(Username,mailid))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"



@app.route("/index", methods=["POST","GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST","GET"])
def chat():
    return render_template("chatbot.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(chatbot.get_response(userText))



@app.route("/res",methods=["POST","GET"])
def res():
    return render_template("quiz.html",res=res)
    if request.method == 'POST' :
        resul=request.form.getlist('info')
        e=resul[0]
        em=e.lower()
        with open("static/abc.txt","w") as file:
            file.write(em)
       
@app.route("/result",methods=["POST","GET"])

def result():
    if request.method == 'POST' :
        with open("static/abc.txt","r") as file:
            em=file.read()
        
        result=request.form.getlist('mycheckbox')
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


if __name__ == "__main__":
    
   
    app.run(debug=True)
    


