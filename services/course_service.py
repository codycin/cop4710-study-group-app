from db import get_db_connection
import sqlite3


def createCourse(title,code):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
                """
                INSERT INTO courses (title, code)
                VALUES (?, ?)
                """,
                (title, code)
            )
        course_id = cursor.lastrowid

        conn.commit()
        return True, "Course created successfully", course_id

    except sqlite3.IntegrityError:
        return False, "Course already exists with code, enroll.", None
    finally:
        cursor.close()
        conn.close()
def get_course_by_id(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, title, code
            FROM courses
            WHERE id = ?
            """,
            (course_id,)
        )

        row = cursor.fetchone()

        if row:
            course = {
                "id": row[0],
                "title": row[1],
                "code": row[2],
            }
            return course
        else:
            return None

    finally:
        cursor.close()
        conn.close()

def get_unassigned_students_for_course(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT s.id, s.username, s.group_size_pref
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            WHERE e.course_id = ?
              AND s.id NOT IN (
                  SELECT gm.student_id
                  FROM group_members gm
                  JOIN study_groups sg ON gm.group_id = sg.id
                  WHERE sg.course_id = ?
              )
            """,
            (course_id, course_id)
        )

        rows = cursor.fetchall()

        students = [
            {
                "id": row[0],
                "username": row[1],
                "group_size_pref": row[2],
            }
            for row in rows
        ]

        return students

    finally:
        cursor.close()
        conn.close()


        


    