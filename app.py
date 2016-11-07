from flask import abort, Flask, render_template, request, redirect, url_for, session
import datetime, os

import db_builder
import hashlib
import story
import user

app = Flask(__name__)

def validate_form(form, required_keys):
    """ Check if a dictionary contains all the required keys """
    return set(required_keys) <= set(form)

#login route
@app.route("/", methods=["POST", "GET"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))

    stories = story.get_stories()
    filtered = story.filter_stories(stories)
    if request.method == "POST":
        # User has submitted a request to add onto a story
        required_keys = ["story_id", "content"]
        if not validate_form(request.form, required_keys):
            return render_template("index.html", message="Malformed request.", category="danger", stories=filtered)

        # Add contribution to the database
        story_id = int(request.form["story_id"])
        content = request.form["content"]

        if len(content) > 150:
            return render_template("index.html", stories=filtered, message="Content should be less than or equal to 150 characters.", category="danger")

        success, message = story.update_story(session["username"], story_id, content)
        category = "success" if success else "danger"

        stories = story.get_stories()
        filtered = story.filter_stories(stories)

        return render_template("index.html", stories=filtered, message=message, category=category)

    return render_template("index.html", stories=filtered)

#create a new account app route
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # User has submitted a request to register an account
        required_keys = ["username", "pass", "passconfirm", "bday"]
        if not validate_form(request.form, required_keys):
            return render_template("register.html", message="Malformed request.", category="danger")

        username = request.form["username"]
        password = request.form["pass"]
        password_confirm = request.form["passconfirm"]
        bday = request.form["bday"]

        if not username.isalnum():
            return render_template("register.html", message="Usernames must contain only alphanumeric characters.", category="danger")

        if password != password_confirm:
            return render_template("register.html", message="Passwords do not match.", category="danger")

        if len(password) < 6:
            return render_template("register.html", message="Password must be at least 6 characters in length.", category="danger")

        if password == password.lower():
            return render_template("register.html", message="Password must contain at least one capitalized letter.", category="danger")

        now = datetime.datetime.now()
        try:
            # dob should be in the format "yyyy-mm-dd"
            dob = map(int, bday.split("-"))
            assert len(dob) == 3
        except:
            return render_template("register.html", message="Invalid birthday.", category="danger")

        dob = datetime.datetime(dob[0], dob[1], dob[2])
        if int((now - dob).days / 365.25) < 13:
            return render_template("register.html", message="Users must be 13 years or older to register for an account.", category="danger")

        if user.get_user(username=username):
            return render_template("register.html", message="Username is already in use.", category="danger")

        user.add_user(username, password, bday)

        return render_template("register.html", message="Account created!", category="success")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # User has submitted a request to login
        required_keys = ["username", "pass"]
        if not validate_form(request.form, required_keys):
            return render_template("login.html", message="Malformed request.", category="danger")

        username = request.form["username"]
        password = hashlib.sha1(request.form["pass"]).hexdigest()

        result = user.get_user(username=username)
        if result:
            if result[2] == password:
                session["username"] = username
                return redirect(url_for("profile"))
            return render_template("login.html", message="Invalid password", category="danger")
        return render_template("login.html", message="Username does not exist...", add_mess="Register a new account?", category="danger")
    return render_template("login.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # User has submitted a request to create a story
        username = session["username"]

        required_keys = ["title", "content"]
        if not validate_form(request.form, required_keys):
            return render_template("create.html", message="Malformed request.", category="danger")

        title = request.form["title"]
        content = request.form["content"]

        if len(content) > 150:
            return render_template("create.html", message="Content should be less than or equal to 150 characters.", category="danger")

        story.create_story(username, title, content)
        return render_template("create.html", message="Story created!", category="success")
    return render_template("create.html")

@app.route("/profile/")
@app.route("/profile/<username>")
def profile(username=None):
    if "username" not in session:
        return redirect(url_for("login"))

    if not username:
        username = session["username"]
    me = username == session["username"]

    uid = user.get_user(username=username)
    if uid:
        uid = uid[0]
        info = user.get_info(uid)
        stories = user.get_stories(uid)
        filtered = story.filter_stories(stories)
        return render_template("profile.html", info=info, stories=filtered, me=me)
    # Invalid user
    abort(404)

@app.route("/editprofile", methods=["GET", "POST"])
def editprofile():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # User has submitted a request to create a story
        username = session["username"]

        required_keys = ["name", "aboutme"]
        if not validate_form(request.form, required_keys):
            return render_template("editprofile.html", message="Malformed request.", category="danger")

        user.update_profile(username, request.form['name'], request.form['aboutme'])
        return redirect(url_for('profile'))
    uid = user.get_user(username=session["username"])[0]
    info = user.get_info(uid)
    return render_template("editprofile.html", info=info)

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
    if not os.path.exists("data.db"):
        db_builder.create_tables()
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
