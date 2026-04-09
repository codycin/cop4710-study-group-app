from db import get_db_connection
import bcrypt
from datetime import datetime


def seed_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Clear tables
        cursor.execute("DELETE FROM appointment_attendees")
        cursor.execute("DELETE FROM appointments")
        cursor.execute("DELETE FROM group_members")
        cursor.execute("DELETE FROM enrollments")
        cursor.execute("DELETE FROM study_groups")
        cursor.execute("DELETE FROM courses")
        cursor.execute("DELETE FROM students")

        cursor.execute("DELETE FROM sqlite_sequence")

        # -------------------------
        # Students (MORE VARIETY)
        # -------------------------
        students = [
            ("alice@fsu.edu", hash_password("password123"), "CS", "student", 4, "alice"),
            ("bob@fsu.edu", hash_password("password123"), "CS", "student", 3, "bob"),
            ("carol@fsu.edu", hash_password("password123"), "IT", "student", 5, "carol"),
            ("david@fsu.edu", hash_password("password123"), "CS", "student", 2, "david"),
            ("emma@fsu.edu", hash_password("password123"), "DS", "student", 4, "emma"),
            ("frank@fsu.edu", hash_password("password123"), "Cyber", "student", 3, "frank"),
            ("grace@fsu.edu", hash_password("password123"), "CS", "student", 2, "grace"),
            ("henry@fsu.edu", hash_password("password123"), "CS", "student", 5, "henry"),
            ("ivy@fsu.edu", hash_password("password123"), "DS", "student", 3, "ivy"),
            ("jack@fsu.edu", hash_password("password123"), "CS", "student", 4, "jack"),
        ]

        cursor.executemany("""
            INSERT INTO students (email, password_hash, major, role, group_size_pref, username)
            VALUES (?, ?, ?, ?, ?, ?)
        """, students)

        # -------------------------
        # Courses
        # -------------------------
        courses = [
            ("Database Systems", "COP4710"),
            ("Software Engineering", "CEN4020"),
        ]

        cursor.executemany("""
            INSERT INTO courses (title, code)
            VALUES (?, ?)
        """, courses)

        # -------------------------
        # Enrollments
        # (ALL students in course 1 → good for auto-match)
        # -------------------------
        enrollments = [(i, 1) for i in range(1, 11)]

        cursor.executemany("""
            INSERT INTO enrollments (student_id, course_id)
            VALUES (?, ?)
        """, enrollments)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # -------------------------
        # Study Groups
        # -------------------------
        study_groups = [
            (1, "SQL Squad", now, 1),
            (1, "Normalization Nation", now, 4),
        ]

        cursor.executemany("""
            INSERT INTO study_groups (course_id, name, created_at, leader_id)
            VALUES (?, ?, ?, ?)
        """, study_groups)

        # -------------------------
        # Group Members
        # -------------------------
        group_members = [
            (1, 1), (1, 2), (1, 4),
            (2, 4), (2, 6),
        ]

        cursor.executemany("""
            INSERT INTO group_members (group_id, student_id)
            VALUES (?, ?)
        """, group_members)

        # -------------------------
        # Appointments (WITH DESCRIPTION)
        # -------------------------
        appointments = [
            ("ER Diagram Review", "09:00", "10:00", 1, 1, 1, "2024-10-01", "Review ER diagrams for project"),
            ("SQL Practice Session", "14:00", "15:30", 2, 1, 1, "2024-10-01", "Practice joins and aggregations"),
            ("Normalization Workshop", "11:00", "12:00", 4, 1, 2, "2024-10-01", "3NF and BCNF walkthrough"),
        ]

        cursor.executemany("""
            INSERT INTO appointments (title, time, end_time, leader_id, course_id, group_id, date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, appointments)

        # -------------------------
        # Appointment Attendees
        # -------------------------
        attendees = [
            (1, 1), (1, 2), (1, 4),
            (2, 1), (2, 2),
            (3, 4), (3, 6),
        ]

        cursor.executemany("""
            INSERT INTO appointment_attendees (appointment_id, student_id)
            VALUES (?, ?)
        """, attendees)

        conn.commit()
        print("🔥 Test data loaded successfully")

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