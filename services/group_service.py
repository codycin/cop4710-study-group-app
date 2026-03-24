from db import get_db_connection
import sqlite3
from datetime import datetime
from flask import session

def search_groups(subject, course_number):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT sg.id, c.subject_code, c.course_number, sg.max_size
        FROM study_group sg
        JOIN course c ON sg.course_id = c.id
        WHERE (? = '' OR c.subject_code = ?)
          AND (? = '' OR c.course_number = ?)
    """

    cursor.execute(query,(subject, subject, course_number, course_number))
    rows = cursor.fetchall()
    conn.close()

    return rows


def join_group(student_id, group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM group_members WHERE group_id = ?", (group_id,))
    count_row = cursor.fetchone()
    current_count = count_row["count"]

    cursor.execute("SELECT max_size FROM study_group WHERE id = ?", (group_id,))
    group_row = cursor.fetchone()

    if not group_row:
        conn.close()
        return False, "Group not found."

    if current_count >= group_row["max_size"]:
        conn.close()
        return False, "This group is already full."

    cursor.execute(
        "INSERT INTO group_members (group_id, student_id) VALUES (?, ?)",
        (group_id, student_id)
    )
    conn.commit()
    conn.close()

    return True, "You joined the group."

def create_group(course_id, name):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        current_datetime = datetime.now()
        cursor.execute(
                """
                INSERT INTO groups (course_id, name, created_at)
                VALUES (?, ?, ?)
                """,
                (course_id, name, current_datetime)
            )
        group_id = cursor.lastrowid

        conn.commit()
        return True, "Group created successfully", group_id

    except sqlite3.IntegrityError:
        return False, "Course already exists with code, enroll.", None
    finally:
        cursor.close()
        conn.close()

