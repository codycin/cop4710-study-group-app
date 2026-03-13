import sqlite3

with open("schema.sql", "r") as f:
    sql = f.read()

conn = sqlite3.connect("database.db")
conn.executescript(sql)
conn.close()

print("Database initialized.")