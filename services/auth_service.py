from db import get_db_connection
import bcrypt
import sqlite3

def register(email, password, major, role, groupSizePref):
    if len(password) < 10:
        return False, "Password must be at least 10 characters", None

    if groupSizePref <= 1:
        return False, "Group size preference must be greater than 1", None

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute(
            """
            INSERT INTO students (email, password, major, role, group_size_pref)
            VALUES (?, ?, ?, ?, ?)
            """,
            (email, hashed_password, major, role, groupSizePref)
        )

        conn.commit()
        student_id = cursor.lastrowid

        return True, "User created successfully", student_id

    except sqlite3.IntegrityError:
        return False, "User already exists", None

    finally:
        cursor.close()
        conn.close()

from db import get_db_connection
import bcrypt

def login(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, password FROM students WHERE email = ?",
            (email,)
        )

        result = cursor.fetchone()

        if not result:
            return False, "User not found", None

        student_id = result[0]
        stored_hash = result[1]

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return True, "Login successful", student_id

        return False, "Invalid password", None

    finally:
        cursor.close()
        conn.close()