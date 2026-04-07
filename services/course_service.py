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


        


    