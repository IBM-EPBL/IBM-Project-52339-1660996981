import numpy as np
from flask import Flask, request, jsonify, render_template
import ibm_db
import pickle
from flask_mysqldb import MySQL
import MySQLdb



#from joblib import load
app = Flask(__name__)

app.config['MYSQL_HOST']="localhost"
app.config['MYSQL_USER']="root"
app.config['MYSQL_PASSWORD']="Karthi@123"
app.config['MYSQL_DB']="ibm"

mysql=MySQL(app)

model = pickle.load(open('decision_model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('login.html')

@app.route("/register",methods=['POST'])
def register():
    email=request.form['inputemail']
    password=request.form['inputpass']
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO email (email,password) VALUES (%s,%s)", (email, password))
    record = cursor.fetchone()
    mysql.connection.commit()
    print("db executed")
    # query="insert into emailverify(email,password) values ('{}','{}');".format(email,password)
    # stmt = ibm_db.exec_immediate(myconn,query)  # do the task
    # while ibm_db.fetch_row(stmt)!=False: #to store the db data
    #     firstname=(ibm_db.result(stmt,0))
    return render_template("login.html")

@app.route("/login",methods=['POST'])
def login():
    email=request.form['inputemail']
    password=request.form['inputpass']
    dbemail=""
    dbpassword=""
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM email WHERE email='{}'".format(email) )
    rec = cursor.fetchone()
    if rec:
        dbemail=rec[0]
        dbpassword=rec[1]
    # query="select password from emailverify where email='{}'".format(email)
    # stmt = ibm_db.exec_immediate(myconn,query)  # do the task
    # while ibm_db.fetch_row(stmt)!=False: #to store the db data
       # dbpass=(ibm_db.result(stmt,0))
    if(dbpassword==password):
        return render_template("index.html")
    else:
        msg="Invalid Username or Password"
        return render_template("login.html",msg=msg)

@app.route('/y_predict',methods=['POST','GET'])
def y_predict():
    '''
    For rendering results on HTML GUI
    '''
    x_test = [[int(x) for x in request.form.values()]]
    print(x_test)
    #sc = load('scalar.save') 
    """model = pickle.load(open('decision_model.pkl', 'rb'))"""
    prediction = model.predict(x_test)
    print(prediction)
    output=prediction[0]
    if(output<=9):
        pred="Worst performance with mileage " + str(prediction[0]) +". Carry extra fuel"
    if(output>9 and output<=17.5):
        pred="Low performance with mileage " +str(prediction[0]) +". Don't go to long distance"
    if(output>17.5 and output<=29):
        pred="Medium performance with mileage " +str(prediction[0]) +". Go for a ride nearby."
    if(output>29 and output<=46):
        pred="High performance with mileage " +str(prediction[0]) +". Go for a healthy ride"
    if(output>46):
        pred="Very high performance with mileage " +str(prediction[0])+". You can plan for a Tour"
        
    
    return render_template('index.html', prediction_text='{}'.format(pred))

@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.y_predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)



