import sqlite3
import hashlib

DATABASE = "data.db"

def add_user(username, password, bday):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "INSERT INTO users VALUES (NULL, ?, ?, ?)"
    c.execute(query, (username, hashlib.sha1(password).hexdigest(), bday,))

    db.commit()
    db.close()

def username_exists(username):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT 1 FROM users WHERE username = ?"
    c.execute(query, (username,))

    result = c.fetchone()
    db.close()
    return result != None

def authenticate(username, password):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT 1 FROM users WHERE username = ? AND password = ?"
    c.execute(query, (username, hashlib.sha1(password).hexdigest()))

    result = c.fetchone()
    db.close()
    return result != None

def get_id(username):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT id FROM users WHERE username = ?"
    c.execute(query, (username,))

    result = c.fetchone()
    db.close()
    return result[0] if result else None

# Get all stories the user contributed to
def get_stories(uid):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT DISTINCT storyid from updates WHERE userid = ?"
    c.execute(query, (uid,))

    result = c.fetchall()
    db.close()
    return [x[0] for x in result] if result else []
