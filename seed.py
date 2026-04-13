from db import get_db_connection
import bcrypt
from datetime import datetime, timedelta


def seed_test_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Clear tables (order matters for foreign keys)
        cursor.execute("DELETE FROM appointment_attendees")
        cursor.execute("DELETE FROM appointments")
        cursor.execute("DELETE FROM group_members")
        cursor.execute("DELETE FROM enrollments")
        cursor.execute("DELETE FROM study_groups")
        cursor.execute("DELETE FROM courses")
        cursor.execute("DELETE FROM students")

        cursor.execute("DELETE FROM sqlite_sequence")

        # -------------------------
        # Students (id 1–15)
        # -------------------------
        students = [
            ("alice@fsu.edu",   hash_password("password123"), "CS",    "student", 4, "alice"),     # 1
            ("bob@fsu.edu",     hash_password("password123"), "CS",    "student", 3, "bob"),       # 2
            ("carol@fsu.edu",   hash_password("password123"), "IT",    "student", 5, "carol"),     # 3
            ("david@fsu.edu",   hash_password("password123"), "CS",    "student", 2, "david"),     # 4
            ("emma@fsu.edu",    hash_password("password123"), "DS",    "student", 4, "emma"),      # 5
            ("frank@fsu.edu",   hash_password("password123"), "Cyber", "student", 3, "frank"),     # 6
            ("grace@fsu.edu",   hash_password("password123"), "CS",    "student", 2, "grace"),     # 7
            ("henry@fsu.edu",   hash_password("password123"), "CS",    "student", 5, "henry"),     # 8
            ("ivy@fsu.edu",     hash_password("password123"), "DS",    "student", 3, "ivy"),       # 9
            ("jack@fsu.edu",    hash_password("password123"), "CS",    "student", 4, "jack"),      # 10
            ("karen@fsu.edu",   hash_password("password123"), "IT",    "student", 3, "karen"),     # 11
            ("leo@fsu.edu",     hash_password("password123"), "CS",    "student", 4, "leo"),       # 12
            ("maya@fsu.edu",    hash_password("password123"), "Cyber", "student", 2, "maya"),      # 13
            ("nick@fsu.edu",    hash_password("password123"), "DS",    "student", 5, "nick"),      # 14
            ("olivia@fsu.edu",  hash_password("password123"), "CS",    "student", 3, "olivia"),    # 15
        ]

        cursor.executemany("""
            INSERT INTO students (email, password_hash, major, role, group_size_pref, username)
            VALUES (?, ?, ?, ?, ?, ?)
        """, students)

        # -------------------------
        # Courses (id 1–4)
        # -------------------------
        courses = [
            ("Database Systems", "COP4710"),           # 1
            ("Software Engineering", "CEN4020"),       # 2
            ("Operating Systems", "COP4610"),          # 3
            ("Intro to Data Science", "ISC4241"),      # 4
        ]

        cursor.executemany("""
            INSERT INTO courses (title, code)
            VALUES (?, ?)
        """, courses)

        # -------------------------
        # Enrollments
        # Spread students across multiple courses
        # -------------------------
        enrollments = [
            # COP4710 – Database Systems (course 1): students 1–10
            (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
            (6, 1), (7, 1), (8, 1), (9, 1), (10, 1),

            # CEN4020 – Software Engineering (course 2): students 2,3,5,8,11,12,13
            (2, 2), (3, 2), (5, 2), (8, 2),
            (11, 2), (12, 2), (13, 2),

            # COP4610 – Operating Systems (course 3): students 1,4,6,7,12,14,15
            (1, 3), (4, 3), (6, 3), (7, 3),
            (12, 3), (14, 3), (15, 3),

            # ISC4241 – Intro to Data Science (course 4): students 5,9,11,14
            (5, 4), (9, 4), (11, 4), (14, 4),
        ]

        cursor.executemany("""
            INSERT INTO enrollments (student_id, course_id)
            VALUES (?, ?)
        """, enrollments)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Use dates relative to today so appointments always look current
        today = datetime.now()
        day1 = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        day3 = (today + timedelta(days=3)).strftime("%Y-%m-%d")
        day5 = (today + timedelta(days=5)).strftime("%Y-%m-%d")
        day7 = (today + timedelta(days=7)).strftime("%Y-%m-%d")
        past1 = (today - timedelta(days=2)).strftime("%Y-%m-%d")

        # -------------------------
        # Study Groups (id 1–5)
        # -------------------------
        study_groups = [
            # COP4710 groups
            (1, "SQL Squad", now, 1),                  # group 1 – leader: alice
            (1, "Normalization Nation", now, 4),        # group 2 – leader: david

            # CEN4020 groups
            (2, "Agile Aces", now, 2),                 # group 3 – leader: bob
            (2, "Sprint Stars", now, 11),              # group 4 – leader: karen

            # COP4610 group
            (3, "Kernel Crew", now, 6),                # group 5 – leader: frank
        ]

        cursor.executemany("""
            INSERT INTO study_groups (course_id, name, created_at, leader_id)
            VALUES (?, ?, ?, ?)
        """, study_groups)

        # -------------------------
        # Group Members
        # -------------------------
        group_members = [
            # SQL Squad (group 1): alice, bob, david
            (1, 1), (1, 2), (1, 4),
            # Normalization Nation (group 2): david, frank, carol, emma
            (2, 4), (2, 6), (2, 3), (2, 5),
            # Agile Aces (group 3): bob, carol, henry
            (3, 2), (3, 3), (3, 8),
            # Sprint Stars (group 4): karen, leo, maya
            (4, 11), (4, 12), (4, 13),
            # Kernel Crew (group 5): frank, grace, olivia, nick
            (5, 6), (5, 7), (5, 15), (5, 14),
        ]

        cursor.executemany("""
            INSERT INTO group_members (group_id, student_id)
            VALUES (?, ?)
        """, group_members)

        # -------------------------
        # Appointments
        # Mix of past and upcoming dates
        # -------------------------
        appointments = [
            # COP4710 / SQL Squad (group 1)
            ("ER Diagram Review",       "09:00", "10:00", 1, 1, 1, past1, "Review ER diagrams for project"),
            ("SQL Joins Practice",      "14:00", "15:30", 2, 1, 1, day1,  "Practice inner/outer joins and subqueries"),
            ("Final Exam Prep",         "10:00", "12:00", 1, 1, 1, day7,  "Go over practice exam and review slides"),

            # COP4710 / Normalization Nation (group 2)
            ("Normalization Workshop",  "11:00", "12:00", 4, 1, 2, day3,  "3NF and BCNF walkthrough"),
            ("Relational Algebra Drill","15:00", "16:30", 6, 1, 2, day5,  "Practice relational algebra problems"),

            # CEN4020 / Agile Aces (group 3)
            ("Sprint Planning Review",  "13:00", "14:00", 2, 2, 3, day1,  "Review user stories and plan sprint 3"),
            ("UML Diagram Session",     "10:00", "11:30", 8, 2, 3, day5,  "Draw class and sequence diagrams"),

            # CEN4020 / Sprint Stars (group 4)
            ("Requirements Review",     "16:00", "17:00", 11, 2, 4, day3, "Finalize functional requirements doc"),

            # COP4610 / Kernel Crew (group 5)
            ("Process Scheduling Lab",  "09:00", "10:30", 6, 3, 5, day1,  "Work through scheduling algorithm problems"),
            ("Deadlock Practice",       "14:00", "15:00", 15, 3, 5, day7, "Bankers algorithm and resource graphs"),
        ]

        cursor.executemany("""
            INSERT INTO appointments (title, time, end_time, leader_id, course_id, group_id, date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, appointments)

        # -------------------------
        # Appointment Attendees
        # -------------------------
        attendees = [
            # ER Diagram Review (appt 1) – SQL Squad members
            (1, 1), (1, 2), (1, 4),
            # SQL Joins Practice (appt 2)
            (2, 1), (2, 2),
            # Final Exam Prep (appt 3)
            (3, 1), (3, 2), (3, 4),
            # Normalization Workshop (appt 4) – Norm Nation members
            (4, 4), (4, 6), (4, 3),
            # Relational Algebra Drill (appt 5)
            (5, 4), (5, 6), (5, 3), (5, 5),
            # Sprint Planning Review (appt 6) – Agile Aces
            (6, 2), (6, 3), (6, 8),
            # UML Diagram Session (appt 7)
            (7, 2), (7, 8),
            # Requirements Review (appt 8) – Sprint Stars
            (8, 11), (8, 12), (8, 13),
            # Process Scheduling Lab (appt 9) – Kernel Crew
            (9, 6), (9, 7), (9, 15),
            # Deadlock Practice (appt 10)
            (10, 6), (10, 7), (10, 14), (10, 15),
        ]

        cursor.executemany("""
            INSERT INTO appointment_attendees (appointment_id, student_id)
            VALUES (?, ?)
        """, attendees)

        conn.commit()
        print("Test data loaded successfully")

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
