import datetime
import sqlite3

import user

DATABASE = "data.db"

def create_story(username, title, content, tags):
    uid = user.get_id(username)

    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "INSERT INTO stories VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)"
    now = int(datetime.datetime.now().strftime("%s"))

    c.execute(query, (username, now, title, content, content, str(uid), tags))
    db.commit()
    db.close()

def update_story(username, story_id, new_text):
    uid = user.get_id(username)

    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    story = get_story(story_id)
    if str(uid) in story[6].split(","):
        return "You already contributed to this story."

    query = "UPDATE stories SET content = content + ?, last_update = ?, contributors = contributors || ? WHERE storyid = ?"

    c.execute(query, (new_text, new_text, "," + str(uid), story_id,))
    db.commit()
    db.close()

    return "Story updated."

def get_story(story_id):
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT * FROM stories WHERE storyid = ?"
    c.execute(query, (story_id,))

    result = c.fetchone()
    db.close()

    return result

def get_stories():
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    query = "SELECT * FROM stories"
    c.execute(query)

    result = c.fetchall()
    db.close()

    return result
