from db import get_db_connection
import bcrypt
from datetime import datetime


def seed_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Clear tables in child-to-parent order
        cursor.execute("DELETE FROM appointment_attendees")
        cursor.execute("DELETE FROM appointments")
        cursor.execute("DELETE FROM group_members")
        cursor.execute("DELETE FROM enrollments")
        cursor.execute("DELETE FROM study_groups")
        cursor.execute("DELETE FROM courses")
        cursor.execute("DELETE FROM students")

        # Reset autoincrement counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='students'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='courses'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='study_groups'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='appointments'")

        # -------------------------
        # Students
        # -------------------------
        students = [
            ("alice@fsu.edu", hash_password("password123"), "Computer Science", "student", 4, "alice"),
            ("bob@fsu.edu", hash_password("password123"), "Computer Science", "student", 3, "bob"),
            ("carol@fsu.edu", hash_password("password123"), "Information Technology", "student", 5, "carol"),
            ("david@fsu.edu", hash_password("password123"), "Computer Science", "student", 2, "david"),
            ("emma@fsu.edu", hash_password("password123"), "Data Science", "student", 4, "emma"),
            ("frank@fsu.edu", hash_password("password123"), "Cybersecurity", "student", 3, "frank"),
        ]

        cursor.executemany(
            """
            INSERT INTO students (email, password_hash, major, role, group_size_pref, username)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            students
        )

        # -------------------------
        # Courses
        # -------------------------
        courses = [
            ("Database Systems", "COP4710"),
            ("Software Engineering", "CEN4020"),
            ("Data Structures", "COP4530"),
            ("Computer Organization", "CDA3100"),
        ]

        cursor.executemany(
            """
            INSERT INTO courses (title, code)
            VALUES (?, ?)
            """,
            courses
        )

        # -------------------------
        # Enrollments
        # student_id, course_id
        # -------------------------
        enrollments = [
            (1, 1), (1, 2),
            (2, 1), (2, 3),
            (3, 2), (3, 4),
            (4, 1), (4, 2),
            (5, 3), (5, 4),
            (6, 1), (6, 4),
        ]

        cursor.executemany(
            """
            INSERT INTO enrollments (student_id, course_id)
            VALUES (?, ?)
            """,
            enrollments
        )

        # -------------------------
        # Study Groups
        # course_id, name, created_at
        # -------------------------
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        study_groups = [
            (1, "SQL Squad", now),
            (1, "Normalization Nation", now),
            (2, "Agile Avengers", now),
            (3, "Pointer Pros", now),
            (4, "Binary Builders", now),
        ]

        cursor.executemany(
            """
            INSERT INTO study_groups (course_id, name, created_at)
            VALUES (?, ?, ?)
            """,
            study_groups
        )

        # -------------------------
        # Group Members
        # group_id, student_id
        # -------------------------
        group_members = [
            (1, 1), (1, 2), (1, 4),
            (2, 4), (2, 6),
            (3, 1), (3, 3), (3, 4),
            (4, 2), (4, 5),
            (5, 3), (5, 5), (5, 6),
        ]

        cursor.executemany(
            """
            INSERT INTO group_members (group_id, student_id)
            VALUES (?, ?)
            """,
            group_members
        )

        # -------------------------
        # Appointments
        # title, time, end_time, leader_id, course_id, group_id
        # -------------------------
        appointments = [
            ("ER Diagram Review", "09:00", "10:00", 1, 1, 1),
            ("SQL Practice Session", "14:00", "15:30", 2, 1, 1),
            ("Normalization Workshop", "11:00", "12:00", 4, 1, 2),
            ("Sprint Planning", "13:00", "14:00", 3, 2, 3),
            ("Linked List Practice", "15:00", "16:00", 2, 3, 4),
            ("Binary Review", "16:30", "17:30", 6, 4, 5),
        ]

        cursor.executemany(
            """
            INSERT INTO appointments (title, time, end_time, leader_id, course_id, group_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            appointments
        )

        # -------------------------
        # Appointment Attendees
        # appointment_id, student_id
        # -------------------------
        appointment_attendees = [
            (1, 1), (1, 2), (1, 4),
            (2, 1), (2, 2),
            (3, 4), (3, 6),
            (4, 1), (4, 3), (4, 4),
            (5, 2), (5, 5),
            (6, 3), (6, 5), (6, 6),
        ]

        cursor.executemany(
            """
            INSERT INTO appointment_attendees (appointment_id, student_id)
            VALUES (?, ?)
            """,
            appointment_attendees
        )

        conn.commit()
        print("Seed data loaded successfully.")

    except Exception as e:
        conn.rollback()
        print(f"Seed failed: {e}")
    finally:
        cursor.close()
        conn.close()

def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")