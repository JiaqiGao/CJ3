import sqlite3

#create the database
database = "data.db"

#add to the database
db = sqlite3.connect(database)

#create a cursor
c = db.cursor()

#create a users table
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, dob INTEGER)")

#create a stories table
c.execute("CREATE TABLE IF NOT EXISTS stories (storyid INTEGER PRIMARY KEY, username TEXT, timestamp INTEGER, title TEXT, content TEXT, last_update TEXT, contributors TEXT, tags TEXT)")

print "table created"

#commit changes to he database
db.commit()

#close the database
db.close()
