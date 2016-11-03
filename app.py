#all the necessary imports
from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import sqlite3
import datetime

import os

#create a Flask app
app = Flask(__name__)

#login route
@app.route("/")
def index():
    # Display a bunch of stories and link to register/login
    return render_template("index.html")

#create a new account app route
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # User has submitted a request to register an account
        usr = request.form["username"]
        pw = request.form["pass"]
        pwc = request.form["passconfirm"]
        bday = request.form["bday"]

        if pw != pwc:
            return render_template("register.html", message="Passwords do not match.")

        db = sqlite3.connect("data.db")
        c = db.cursor()
        c.execute("SELECT username from users where username=?", (usr,))
        if c.fetchone():
            return render_template("register.html", message="That username is taken.")

        hashed_pw = hashlib.sha1(pw).hexdigest()
        # Notes to everyone:
        # Using sqlite3's parameter substitution protects us from sql injections
        # sqlite will auto increment the id
        c.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)", (usr, hashed_pw, bday,))
        db.commit()
        return render_template("register.html", message="Account successfully created!")
    else:
        # User is viewing the page
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["pass"]
        hashed_pw = hashlib.sha1(password).hexdigest()
        # Check to see if a user exists with that username/password combo
        db = sqlite3.connect("data.db")
        c = db.cursor()
        c.execute("SELECT password from users where username=?", (username,))
        match = c.fetchall()
        if match[0][0] == hashed_pw:
             session["username"] = username
             return redirect(url_for("index"))
        return render_template("login.html", message="Invalid credentials")
    else:
        return render_template("login.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    d = sqlite3.connect("data.db")
    c = d.cursor()

    #updating each table input
    username = session["username"]

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    content = request.form['content']
    last_update = ''
    contributors = ''
    tags = request.form['tags']

    q = "INSERT INTO stories VALUES(NULL, ?, ?, ?, ?, ?, ?)"
    # c.execute(q, (username, timestamp, content, last_update, contributors, tags))

@app.route("/contribute", methods=["GET", "POST"])
def contribute():
    if request.method == "POST":
        # Add contribution to the database
        story_id = request.form["story_id"]

        d = sqlite3.connect("data.db")
        c = d.cursor()

        # find row containing our story
        c.execute("SELECT * from stories WHERE storyid=?", (story_id,))

        #set variables to new values
        results = c.fetchall()[0]
        content = results[3] + request['contribution']
        last_update = request['contribution']
        contributors = results[5] + "," + session['username']
        tags = results[6] + "," + request['tags']

        # update the values in the database
        q = "UPDATE stories SET content=?, last_update=?, contributors=?, tags=? WHERE storyid=?"
        # c.execute(q, (content, last_update, contributors, tags, storyid,))

        return render_template("contribute.html")
    else:
        # View all stories
        stories = []
        return render_template("contribute.html", stories=stories)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    # Profile
    pass

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.context_processor
def inject_username():
    # inject the username into each template, so we can render the navbar correctly.
    if session.get("username"):
        return dict(username=session["username"])
    return dict()

if __name__=="__main__":
    app.debug = True

    # Generate and store secret key if it doesn't exist
    with open(".secret_key", "a+b") as f:
        secret_key = f.read()
        if not secret_key:
            secret_key = os.urandom(64)
            f.write(secret_key)
            f.flush()
        app.secret_key = secret_key
        f.close()

    app.run()
