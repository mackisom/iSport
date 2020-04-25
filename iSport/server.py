from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt   
from datetime import datetime 
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
schema="mydb"
app.secret_key="mackenziafdafdlka"
email_check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    if 'user_id' in session:
        session.pop('user_id')
    return render_template("index.html")

@app.route('/register', methods=["POST"])
def register():
    if len(request.form['first_name']) <2:
        flash("First name must contain at least two characters")
    if len(request.form['last_name']) <2:
        flash ("Last name must contain at least two characters")

    if len(request.form['email'])<1:
        flash("Email is required")
    elif not email_check.match(request.form['email']):
        flash("Invalid email address")
    else:
        mysql = connectToMySQL(schema)
        query = "SELECT * FROM user WHERE email = %(email)s;"
        data = {
            "email":request.form['email']
        }
        user = mysql.query_db(query,data)
        if user:
            flash('Email is in use')

    if len(request.form['password']) < 8:
        flash("Password must contain at least 8 characters")
    elif request.form['password'] != request.form['cpassword']:
        flash("Password and Confirm PW fields do not match")

    if '_flashes' not in session:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL(schema)
        query = "INSERT INTO user (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fname)s, %(lname)s, %(email)s, %(pass)s, NOW(), NOW());"
        data = {
            "fname":request.form['first_name'],
            "lname":request.form['last_name'],
            "email":request.form['email'],
            "pass":pw_hash
        }
        new_user = mysql.query_db(query,data)
        if new_user:
            flash("Registration successful")
    return redirect('/')

@app.route('/login', methods=["POST"])
def login():
    if len(request.form['email']) < 1 or len(request.form['password']) < 1:
        flash("Email and Password is required")

    mysql = connectToMySQL(schema)
    query = "SELECT * FROM user WHERE email = %(email)s;"
    data = {
        "email":request.form['email']
    }
    user = mysql.query_db(query,data)
    if user:
        if bcrypt.check_password_hash(user[0]['password'],request.form['password']):
           session['user_id'] = user[0]['id']
           session['fname'] = user[0]['first_name']
           return redirect('/dashboard')
        else:
            flash("Email and password do not match")
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def event():
    if 'user_id' not in session: 
        return redirect('/')
    mysql = connectToMySQL(schema)
    query = "SELECT * FROM event WHERE user_id = %(user)s;"
    data = {
        'user':session['user_id']
    }
    user_event = mysql.query_db(query,data)
    return render_template('dashboard.html', event=user_event)

@app.route('/event/new')
def new():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('new.html')


if __name__ =="__main__":
    app.run(debug=True)

   