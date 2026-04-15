import sqlite3

DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    #Courses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL
        )
    """)
    #Appointments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            leader_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (leader_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (group_id) REFERENCES study_groups(id)

        )
    """)
    #Enrollments in courses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            student_id INTEGER,
            course_id INTEGER,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)
    #Study groups
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            leader_id INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (leader_id) REFERENCES students(id)
        )
    """)
    #Appointment attendees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment_attendees (
            appointment_id INTEGER,
            student_id INTEGER,
            PRIMARY KEY (appointment_id, student_id),
            FOREIGN KEY (appointment_id) REFERENCES appointments(id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    #group members
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            group_id INTEGER,
            student_id INTEGER,
            PRIMARY KEY (group_id, student_id),
            FOREIGN KEY (group_id) REFERENCES study_groups(id),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()