#all the necessary imports
from flask import Flask, render_template, request, redirect, url_for, session
import datetime, os

import db_builder
import hashlib
import story
import user

#create a Flask app
app = Flask(__name__)

def validate_form(form, required_keys):
    """ Check if a dictionary contains all the required keys """
    return set(required_keys) <= set(form)

#login route
@app.route("/")
def index():
    if 'username' in session:
        # Display stories that the user has contributed to
        uid = user.get_user(username=session["username"])[0]
        stories = user.get_stories(uid)
        filtered = story.filter_stories(stories)
        return render_template("index.html", stories=filtered)
    return render_template("login.html")

#create a new account app route
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # User has submitted a request to register an account
        required_keys = ["username", "pass", "passconfirm", "bday"]
        if not validate_form(request.form, required_keys):
            return render_template("register.html", message="Malformed request.")

        username = request.form["username"]
        password = request.form["pass"]
        password_confirm = request.form["passconfirm"]
        bday = request.form["bday"]

        if password != password_confirm:
            return render_template("register.html", message="Passwords do not match.")

        if len(password) < 6:
            return render_template("register.html", message="Password must be at least 6 characters in length")

        if password == password.lower():
            return render_template("register.html", message="Password must contain at least one capitalized letter")

        now = datetime.datetime.now()
        try:
            dob = map(int, bday.split("-"))
        except:
            return render_template("register.html", message="Invalid birthday.")

        if len(dob) != 3:
            return render_template("register.html", message="Invalid birthday.")

        dob = datetime.datetime(dob[0], dob[1], dob[2])
        if int((now - dob).days / 365.25) < 13:
            return render_template("register.html", message="Users must be 13 years or older to register for an account.")

        if user.get_user(username=username):
            return render_template("register.html", message="Username is already in use.")

        user.add_user(username, password, bday)

        return render_template("login.html", message="Account successfully created! You can log in now!")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # User has submitted a request to login
        required_keys = ["username", "pass"]
        if not validate_form(request.form, required_keys):
            return render_template("login.html", message="Malformed request.")

        username = request.form["username"]
        password = hashlib.sha1(request.form["pass"]).hexdigest()

        result = user.get_user(username=username, password=password)
        if result:
            session["username"] = username
            return redirect(url_for("index"))
        return render_template("login.html", message = "Invalid credentials.")
    return render_template("login.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # User has submitted a request to create a story
        username = session["username"]

        required_keys = ["title", "content", "tags"]
        if not validate_form(request.form, required_keys):
            return render_template("create.html", message="Malformed request.")

        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"]

        story.create_story(username, title, content, tags)
        return render_template("create.html", message="Story created!")
    return render_template("create.html")

@app.route("/contribute", methods=["GET", "POST"])
def contribute():
    if "username" not in session:
        return redirect(url_for("login"))

    message = ""
    if request.method == "POST":
        # User has submitted a request to add onto a story
        required_keys = ["story_id", "content"]
        if not validate_form(request.form, required_keys):
            return render_template("contribute.html", message="Malformed request.")

        # Add contribution to the database
        story_id = int(request.form["story_id"])
        content = request.form["content"]

        message = story.update_story(session["username"], story_id, content)

    stories = story.get_stories()
    filtered = story.filter_stories(stories)
    return render_template("contribute.html", stories=filtered, message=message)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.context_processor
def inject_username():
    """ Inject the username into each template, so we can render the navbar correctly. """
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

    app.run()
