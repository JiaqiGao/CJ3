import sqlite3

#create the database
database = "data.db"

#add to the database
db = sqlite3.connect(database)

#create a cursor
c = db.cursor()

#create a users table
c.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT, dob INTEGER)")

#create a stories table
c.execute("CREATE TABLE stories (storyid INTEGER, authorid INTEGER, timestamp INTEGER, content TEXT, last_update TEXT, contributors TEXT, tags TEXT)")

#commit changes to he database
db.commit()

#close the database
db.close()
