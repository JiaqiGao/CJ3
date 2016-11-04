#all the necessary imports
from flask import Flask, render_template, request, redirect, url_for, session
import datetime, os

import story
import user

#create a Flask app
app = Flask(__name__)

#login route
@app.route("/")
def index():
    if 'username' in session:
        return render_template("index.html", user=session["username"])
    return render_template("login.html")

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

        if len(pw) < 6:
            return render_template("register.html", message="Password must be at least 6 characters in length")

        if pw == pw.lower():
            return render_template("register.html", message="Password must contain at least one capitalized letter")

        now = datetime.datetime.now()
        dob = bday.split("-")
        if len(dob) != 3:
            return render_template("register.html", message="Invalid birthday.")

        dob = datetime.datetime(int(dob[0]), int(dob[1]), int(dob[2]))
        if int((now - dob).days / 365.25) < 13:
            return render_template("register.html", message="Users must be 13 years or older to register for an account.")

        if user.username_exists(usr):
            return render_template("register.html", message="Username is already in use.")

        user.add_user(usr, pw, bday)

        return render_template("register.html", message="Account successfully created!")
    else:
        # User is viewing the page
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["pass"]

        success = user.authenticate(username, password)
        if success:
            session["username"] = username
            return redirect(url_for("index"))
        return render_template("login.html", message = "Invalid credentials.")
    else:
        return render_template("login.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        username = session["username"]
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"]

        story.create_story(username, title, content, tags)

        return render_template("create.html", message="Story created!")
    else:
        return render_template("create.html")

@app.route("/contribute", methods=["GET", "POST"])
def contribute():
    if "username" not in session:
        return redirect(url_for("login"))

    # View all stories
    stories = story.get_stories()
    filtered = []
    for s in stories:
        filtered.append({
            "story_id": s[0],
            "timestamp": datetime.datetime.fromtimestamp(s[2]).strftime("%B %d, %Y %I:%M %p"),
            "title": s[3],
            "last_update": s[5]
        })

    if request.method == "POST":
        # Add contribution to the database
        story_id = request.form["story_id"]
        content = request.form["content"]

        message = story.update_story(session["username"], story_id, content)

        return render_template("contribute.html", stories=filtered, message=message)
    else:
        return render_template("contribute.html", stories=filtered)

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
