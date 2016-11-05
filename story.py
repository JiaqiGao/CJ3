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

    for story in user.get_stories(uid):
        if story_id in story:
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

    return result if result else []

def filter_stories(stories):
    filtered = []
    for story in stories:
        story_id = story[0]
        title = story[1]
        updates = get_updates(story_id)
        content = "".join([update[4] for update in updates])
        last_updated = datetime.datetime.fromtimestamp(updates[-1][3]).strftime("%B %d, %Y %I:%M %p")
        last_update = updates[-1][4]

        filtered.append({
            "story_id": story_id,
            "timestamp": last_updated,
            "title": title,
            "last_update": last_update,
            "content": content
        })

    return filtered
