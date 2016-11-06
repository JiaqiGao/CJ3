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

def get_user(**kwargs):
    if not kwargs:
        return None

    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    criterion = []
    params = []
    for k,v in kwargs.items():
        criterion.append("%s = ?" % k)
        params.append(str(v))

    query = "SELECT * FROM users WHERE %s" % " AND ".join(criterion)
    c.execute(query, params)

    result = c.fetchone()
    db.close()
    return result

# Get all stories the user contributed to
def get_stories(uid):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT DISTINCT stories.storyid,stories.title from updates,stories WHERE userid = ? AND updates.storyid = stories.storyid"
    c.execute(query, (uid,))

    result = c.fetchall()
    db.close()
    return result if result else []

def create_profile(uid):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
