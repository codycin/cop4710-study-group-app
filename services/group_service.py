from db import get_db_connection
import sqlite3
from datetime import datetime


def search_groups(course_code=""):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            sg.id,
            sg.name,
            sg.course_id,
            c.title AS course_title,
            c.code AS course_code,
            COUNT(gm.student_id) AS member_count
        FROM study_groups sg
        JOIN courses c ON sg.course_id = c.id
        LEFT JOIN group_members gm ON gm.group_id = sg.id
        WHERE (? = '' OR c.code LIKE ?)
        GROUP BY sg.id, sg.name, sg.course_id, c.title, c.code
        ORDER BY sg.created_at DESC
    """

    like_code = f"%{course_code}%"
    cursor.execute(query, (course_code, like_code))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def join_group(student_id, group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not student_id:
            return False, "You must be logged in to join a group."

        cursor.execute(
            "SELECT id, name FROM study_groups WHERE id = ?",
            (group_id,)
        )
        group = cursor.fetchone()

        if not group:
            return False, "Group not found."

        cursor.execute(
            "SELECT 1 FROM students WHERE id = ?",
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            return False, "Student not found."

        cursor.execute(
            "INSERT INTO group_members (group_id, student_id) VALUES (?, ?)",
            (group_id, student_id)
        )

        conn.commit()
        return True, "You joined the group."

    except sqlite3.IntegrityError:
        return False, "You are already in this group."

    finally:
        cursor.close()
        conn.close()

def leave_group(student_id, group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not student_id:
            return False, "You must be logged in to leave a group."

        cursor.execute(
            "SELECT id, name FROM study_groups WHERE id = ?",
            (group_id,)
        )
        group = cursor.fetchone()

        if not group:
            return False, "Group not found."

        cursor.execute(
            "SELECT 1 FROM students WHERE id = ?",
            (student_id,)
        )
        student = cursor.fetchone()

        if not student:
            return False, "Student not found."

        cursor.execute(
            """
            SELECT 1
            FROM group_members
            WHERE group_id = ? AND student_id = ?
            """,
            (group_id, student_id)
        )
        membership = cursor.fetchone()

        if not membership:
            return False, "You are not in this group."

        cursor.execute(
            """
            DELETE FROM group_members
            WHERE group_id = ? AND student_id = ?
            """,
            (group_id, student_id)
        )

        conn.commit()
        return True, "You left the group."

    finally:
        cursor.close()
        conn.close()


def create_group(course_id, name, student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not course_id or not name:
            return False, "Course and group name are required.", None

        # Verify this student is enrolled in the selected course
        cursor.execute(
            """
            SELECT 1
            FROM enrollments
            WHERE student_id = ? AND course_id = ?
            """,
            (student_id, course_id)
        )
        enrollment = cursor.fetchone()

        if not enrollment:
            return False, "You can only create groups for courses you're enrolled in.", None

        cursor.execute(
            """
            INSERT INTO study_groups (course_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            (course_id, name, datetime.now().isoformat())
        )

        group_id = cursor.lastrowid
        conn.commit()
        return True, "Group created successfully.", group_id

    except sqlite3.IntegrityError:
        return False, "Could not create group.", None

    finally:
        cursor.close()
        conn.close()

def get_student_courses(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.id, c.title, c.code
        FROM courses c
        JOIN enrollments e ON e.course_id = c.id
        WHERE e.student_id = ?
        ORDER BY c.code
        """,
        (student_id,)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_my_groups(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            sg.id,
            sg.name,
            sg.created_at,
            c.id AS course_id,
            c.code AS course_code,
            c.title AS course_title,
            (
                SELECT COUNT(*)
                FROM group_members gm2
                WHERE gm2.group_id = sg.id
            ) AS member_count
        FROM group_members gm
        JOIN study_groups sg ON gm.group_id = sg.id
        JOIN courses c ON sg.course_id = c.id
        WHERE gm.student_id = ?
        ORDER BY sg.created_at DESC
        """,
        (student_id,)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows