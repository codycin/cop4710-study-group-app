import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(courses)")
print("courses columns:")
for row in cursor.fetchall():
    print(row)

cursor.execute("PRAGMA index_list(courses)")
print("\ncourses indexes:")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='courses'")
print("\ncourses create statement:")
print(cursor.fetchone())

cursor.close()
conn.close()