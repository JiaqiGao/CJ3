import datetime
import sqlite3

import user

DATABASE = "data.db"

def create_story(username, title, content, tags):
    uid = user.get_id(username)

    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "INSERT INTO stories VALUES (NULL, ?, ?)"
    c.execute(query, (title, tags,))

    # Fetch primary key of newly inserted row
    storyid = c.lastrowid

    now = int(datetime.datetime.now().strftime("%s"))
    query = "INSERT INTO updates VALUES (NULL, ?, ?, ?, ?)"
    c.execute(query, (storyid, uid, now, content,))

    db.commit()
    db.close()

def update_story(username, story_id, content):
    uid = int(user.get_id(username))

    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    if story_id in user.get_stories(uid):
        return "You already contributed to this story."

    query = "INSERT INTO updates VALUES (NULL, ?, ?, ?, ?)"
    now = int(datetime.datetime.now().strftime("%s"))

    c.execute(query, (story_id, uid, now, content,))
    db.commit()
    db.close()

    return "Story updated."

def get_stories():
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT * FROM stories"
    c.execute(query)

    result = c.fetchall()
    db.close()

    return result

def get_updates(story_id):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT * FROM updates WHERE storyid = ? ORDER BY timestamp ASC"
    c.execute(query, (story_id,))

    result = c.fetchall()
    db.close()

    return result
