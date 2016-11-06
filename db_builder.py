import sqlite3

DATABASE = "data.db"

def create_tables():
    db = sqlite3.connect(DATABASE)
    c = db.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, dob INTEGER, name TEXT, aboutme TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS stories (storyid INTEGER PRIMARY KEY, title TEXT, tags TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS updates (id INTEGER PRIMARY KEY, storyid INTEGER, userid INTEGER, timestamp INTEGER, content TEXT)")

    db.commit()
    db.close()
