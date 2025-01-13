import os
import flask
from flask import render_template, request, jsonify, session
from flask import jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_session import Session
from keras.models import Sequential, load_model
from keras.layers import Dense
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
import matplotlib.pyplot as plt


app = flask.Flask(__name__, template_folder='Templates')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#code for connection
app.config['MYSQL_HOST'] = 'localhost'#hostname
app.config['MYSQL_USER'] = 'root'#username
app.config['MYSQL_PASSWORD'] = ''#password
app.config['MYSQL_DB'] = 'poverty_satelight'#database name

mysql = MySQL(app)
@app.route('/')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
            return(flask.render_template('index.html'))

@app.route('/joinus', methods=['GET', 'POST'])
def joinus():
    if flask.request.method == 'GET':
            return(flask.render_template('joinus.html'))
        
@app.route('/about', methods=['GET', 'POST'])
def about():
    if flask.request.method == 'GET':
        return(flask.render_template('about.html'))
    
@app.route('/service', methods=['GET', 'POST'])
def service():
    if flask.request.method == 'GET':
        return(flask.render_template('service.html'))
    
@app.route('/ourai', methods=['GET', 'POST'])
def ourai():
    if flask.request.method == 'GET':
        return(flask.render_template('ourai.html'))
    
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if flask.request.method == 'GET':
        return(flask.render_template('contact.html'))
    
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if flask.request.method == 'GET':
        return(flask.render_template('admin.html'))
    
@app.route('/aidiagnosis', methods=['GET', 'POST'])
def aidiagnosis():
    if flask.request.method == 'GET':
        return(flask.render_template('aidiagnosis.html'))
    

@app.route('/getrecords', methods=['GET', 'POST'])
def getrecords():        
    if flask.request.method == 'POST':
        userid = session.get("userid")
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM history WHERE userid="'+str(userid)+'"')
        result = cursor.fetchall();
    return jsonify(result)


model = load_model('poverty_detect_satelight.h5')

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array

# Function to make predictions
def predict(image_path):
    img = preprocess_image(image_path)
    prediction = model.predict(img)
    pred = np.argmax(prediction)
    
    return pred

class_names = [
  'Poverty',
  'Non-Poverty'
]

classification_map  = {
  "Poverty": "Areas identified as poverty-stricken from satellite imagery often exhibit signs such as sparse infrastructure, informal settlements, and agricultural practices indicative of subsistence living. These regions may lack access to basic amenities like paved roads, electricity, and sanitation, reflecting economic challenges and disparities in resource distribution. The presence of makeshift dwellings and limited vegetation cover further underscores the socio-economic hardships faced by residents. Poverty-stricken areas often show lower levels of economic activity and investment, contributing to cycles of poverty that can be challenging to break without targeted interventions aimed at improving infrastructure, education, and access to healthcare services.",
  "Non-Poverty": "Non-poverty areas, observed through satellite imagery, typically show characteristics such as dense urbanization, developed infrastructure, and higher vegetation indices. These features signify better living standards, economic activity, and access to essential services. Urbanized regions in non-poverty areas often boast well-maintained roads, modern buildings, and green spaces indicative of environmental health and urban planning. Higher vegetation indices reflect agricultural productivity and land use diversity, supporting sustainable livelihoods and economic growth. Non-poverty areas generally exhibit higher levels of socio-economic development and resilience to economic shocks compared to poverty-stricken regions."
}

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if flask.request.method == 'GET':
        return(flask.render_template('detect.html'))
    if flask.request.method == 'POST':
       filename = request.form['filename']
      
       input_path  = './static/inputfiles/'+filename
      
       con = mysql.connect
       con.autocommit(True)
       cursor = con.cursor(MySQLdb.cursors.DictCursor)
       
       pred = predict(input_path)
       predicted_class = class_names[pred]
       desc = classification_map[predicted_class]
       userid = session.get('userid')
       
       history = 'INSERT INTO history(userid, sample, prediction) VALUES("'+str(userid)+'","'+str(filename)+'","'+str(predicted_class)+'")'
       cursor.execute(history)
       mysql.connect.commit()
       
    toReturn = {"filename": filename, "prediction":predicted_class, "desc":desc} 
    return jsonify(toReturn)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        phone           = request.form['signphone']
        password        = request.form['signpassword']
        msg = 0
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        
        qry = 'SELECT * FROM userdetail WHERE phone="'+phone+'" AND password="'+password+'"'
        result = cursor.execute(qry)
        result = cursor.fetchone()
        
        if result is not None:
            if result["adminapproved"] != 1:
                msg = "2"
            elif result["adminapproved"] == 1:
                msg = "1"
                session["userid"]   = result["userid"]
                session["username"]   = result["username"]
                session["usermail"]   = result["email"]
        else:
           msg = "0"           
    return jsonify(msg)

@app.route('/updateuserrecord', methods=['GET', 'POST'])
def updateuserrecord():
    if flask.request.method == 'POST':    
        userid    = request.form['userid']
        step      = request.form['step']
        
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        qry = 'UPDATE userdetail SET adminapproved ='+step+' WHERE userid ='+userid
        cursor.execute(qry)
        msg = "1"
        mysql.connect.commit()
    return msg

#User Login   
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if flask.request.method == 'GET':
        return(flask.render_template('admin.html'))
    if flask.request.method == 'POST':
        msg=''
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            con = mysql.connect
            con.autocommit(True)
            cursor = con.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM admin_details WHERE admin_name = % s and password = %s', (username, password,))
            result = cursor.fetchone()
            print(result)
        if result:
            msg = "1"
        else:
           msg = "0"
    return msg
    

@app.route('/getuserrecords', methods=['GET', 'POST'])
def getuserrecords():
    if request.method == 'POST':
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM userdetail WHERE adminapproved = 0')
        result = cursor.fetchall()
        
        return jsonify(result)
    
@app.route('/gethistory', methods=['GET', 'POST'])
def gethistory():
    if request.method == 'POST':
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM history')
        result = cursor.fetchall()
        
        return jsonify(result)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if flask.request.method == 'GET':
        session.pop('userid', None)
        session.pop('username', None)
        session.pop('usermail', None)
        
        return(flask.render_template('index.html'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        username  = request.form['regusername']
        phone        = request.form['regphone']
        email        = request.form['regemail']
        usedfor      = request.form['usingfor']
        password     = request.form['regpassword']
        
        con = mysql.connect
        con.autocommit(True)
        cursor = con.cursor(MySQLdb.cursors.DictCursor)
        
        qry = 'SELECT * FROM userdetail WHERE phone="'+phone+'" AND password="'+password+'"'
        result = cursor.execute(qry)
        result = cursor.fetchone()
        
        if result:
            msg = '2'
        else:
            cursor.execute('INSERT INTO userdetail VALUES (NULL, %s, %s, %s, %s, %s, %s, NULL)', (username, email, phone, usedfor, password, '0', ))
            mysql.connect.commit()
            msg = '1'
        
        return msg

if __name__ == '__main__':
    app.run(debug=False)