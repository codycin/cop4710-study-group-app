from db import get_db_connection
import sqlite3

def enrollStudent(student_id, course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM courses WHERE id = ?",
            (course_id,)
        )
        if cursor.fetchone() is None:
            return False, "Course does not exist"

        cursor.execute(
            "SELECT 1 FROM students WHERE id = ?",
            (student_id,)
        )
        if cursor.fetchone() is None:
            return False, "Student does not exist"

        cursor.execute(
            "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
            (student_id, course_id)
        )

        conn.commit()
        return True, "You enrolled in the course."

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            return False, "Already enrolled"
        return False, "Database integrity error"

    finally:
        cursor.close()
        conn.close()

def unenrollStudent(student_id, course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM courses WHERE id = ?",
            (course_id,)
        )
        if cursor.fetchone() is None:
            return False, "Course does not exist"

        cursor.execute(
            "SELECT 1 FROM students WHERE id = ?",
            (student_id,)
        )
        if cursor.fetchone() is None:
            return False, "Student does not exist"
        
        cursor.execute(
            "DELETE FROM enrollments WHERE student_id = ? AND course_id = ?",
            (student_id, course_id)
        )
        
        if(cursor.rowcount == 0):
            return False, "Student is not in course"
        
        conn.commit()
        return True, "You've unenrolled from the course"

    finally:
        cursor.close()
        conn.close()
