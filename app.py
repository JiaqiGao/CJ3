#all the necessary imports
from flask import Flask, render_template, request, redirect, url_for, session
import random, hashlib

#create a Flask app
app = Flask(__name__)

#login route
@app.route("/", methods=['POST', 'GET'])
def login():
    #click if the user has a preexisting session
    if "user" in session:
        #if there was a session but you've logged out, remove the user from teh session
        if "logout" in request.form:
            session.pop("user")
        #if there wasn't already a session go to the /results app route
        else:
            return redirect("/results")
    #return the login page
    return render_template("login.html")

#create a new account app route
@app.route("/register")
def newAccount():
    #go to the register html page
    return render_template("register.html")

#create a "you've successfully registered for an account" app route
@app.route("/success", methods=['POST'])
def creationSuccess():
    #get username
    usr = request.form['username']
    #get password
    pw = request.form['pass']
    #confirm password
    pwc = request.form['passconfirm']
    #get birthday
    bday = request.form['bday']
    #if password and confirmed password are not the same
    if pw != pwc:
        return "<h1>Passwords did not match!</h1><a href='/register'>Try again</a>"
    #if the username already exists
    if usr in parseCSV("accounts.csv"):
        return "<h1>Username already exists! use</h1><a href='/register'>Try again</a>"
    #if the birthday indicates that the user is not old enough to create an account
    ###JAMES WILL PUT THE STATEMENT HERE###
    #otherwise, add the new user
    accounts = open("accounts.csv", "a")
    accounts.write(usr + ',' + hashlib.sha1(pw).hexdigest() + '\n')
    return "<h4>Your account has been successfully created</h4>" + render_template("login.html")

#we need to be able to break apart the elements of the csv file to check the usernames and passwords
def parseCSV(location):
    #string of the accounts csv file
    slogin = open("accounts.csv", "r")
    slogin = slogin.read()
    #keep the usernames paired with their respective passwords
    pairs = slogin.split("\n")
    logins = {}
    print "\n"
    #for each pair of usernames and passwords if the length of the pair is greater than 1 (you have a username, a comma, and a password) separate at the comma
    for pair in pairs:
        if len(pair)>1:
            logins[pair[0:pair.index(',')]] = pair[pair.index(",")+1:]
    print "\n"
    #return the dict of logins
    return logins

#create a results app route
@app.route("/results", methods=['GET', 'POST'])
def results():
    #if your user has a session
    if "user" in session:
        #go to the home page html page, mark the success variable as true, and note which user is in session
        return render_template("home.html", success=True, user=session["user"])
    else:
        #store the dict of logins from the csv file
        logins = parseCSV("accounts.csv")
        #hash the inputted password
        myHash = hashlib.sha1(request.form['pass'])
        #save the inputted username
        usr = request.form['username']
        #save the inputted password
        pw = request.form['pass']
        #if the username exists and the hashed inputted password is the same as the hashed password linked to the username
        if usr in logins and logins[usr] == myHash.hexdigest():
            #save the current user in a session
            session["user"] = usr
            #return the home page for the user
            return render_template("home.html", success=True, user=session["user"])
        else:
            #if the username is not in the csv file
            if usr not in logins:
                #redirect and go to the wrong user problem
                return render_template("home.html", success=False, problem="wronguser")
            else:
                #redirect and go to the wrong password problem
                return render_template("home.html", success=False, problem="wrongpassword")

#for debugging
if __name__=="__main__":
    app.debug = True
    #put the secret key in!!
    app.secret_key = "123"
    app.run()
