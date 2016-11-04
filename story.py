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
    uid = user.get_id(username)[0]

    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    story = get_story(story_id)
    content = story[4] + new_text
    contributors = story[6] + "," + str(uid)

    query = "UPDATE stories SET content = ?, last_update = ?, contributors = ? WHERE storyid = ?"

    c.execute(query, (content, new_text, contributors, story_id,))
    db.commit()
    db.close()

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
