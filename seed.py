from db import get_db_connection
import bcrypt
import random
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

        # =============================================
        # COURSES — Real FSU CS catalog courses (id 1-12)
        # =============================================
        courses = [
            ("Theory and Structure of Databases", "COP4710"),                    # 1
            ("Object-Oriented Programming", "COP3330"),                          # 2
            ("Computer Organization I", "CDA3100"),                              # 3
            ("Operating Systems and Concurrent Programming", "COP4610"),         # 4
            ("Data Structures, Algorithms, and Generic Programming", "COP4530"), # 5
            ("Software Engineering I", "CEN4020"),                               # 6
            ("Programming Languages", "COP4020"),                                # 7
            ("Theory of Computation", "COT4420"),                                # 8
            ("Computer Organization II", "CDA3101"),                             # 9
            ("Introduction to Programming", "COP3363"),                          # 10
            ("Ethics in Computer Science", "CIS4250"),                           # 11
            ("Complexity and Analysis of Data Structures and Algorithms", "COP4531"),  # 12
        ]

        cursor.executemany("""
            INSERT INTO courses (title, code) VALUES (?, ?)
        """, courses)

        # =============================================
        # STUDENTS — 120 synthetic students (id 1-120)
        # All passwords are: password123
        # =============================================
        first_names = [
            "alice", "bob", "carol", "david", "emma", "frank", "grace", "henry",
            "ivy", "jack", "karen", "leo", "maya", "nick", "olivia", "peter",
            "quinn", "rosa", "sam", "tina", "uma", "victor", "wendy", "xander",
            "yara", "zach", "amber", "brian", "chloe", "derek", "elena", "felix",
            "gina", "hector", "iris", "james", "kara", "logan", "mia", "nolan",
            "paige", "ray", "sara", "troy", "ursula", "vince", "willa", "xavier",
            "yvette", "zane", "adam", "beth", "carl", "diana", "ethan", "fiona",
            "grant", "haley", "ivan", "julia", "keith", "luna", "marco", "nadia",
            "omar", "priya", "reid", "sonia", "theo", "una", "val", "wade",
            "xena", "yasmin", "zeke", "aria", "blake", "clara", "dante", "elise",
            "finn", "gia", "hugo", "isla", "joel", "kylie", "lance", "mona",
            "neal", "opal", "pablo", "rue", "sean", "tara", "umar", "vera",
            "wyatt", "ximena", "yolanda", "zara", "alex", "bianca", "colton",
            "demi", "evan", "freya", "gavin", "holly", "ian", "jess", "kai",
            "leah", "miles", "nora", "owen", "piper", "riley", "stella", "ty", "liam",
        ]

        majors = [
            "Computer Science", "Information Technology", "Data Science",
            "Cybersecurity", "Software Engineering",
        ]
        group_size_options = [2, 3, 3, 4, 4, 4, 5, 5]

        # Hash once and reuse — saves time since bcrypt is slow
        hashed_pw = hash_password("password123")

        students = []
        for i, name in enumerate(first_names):
            email = f"{name}{i + 1}@fsu.edu"
            major = majors[i % len(majors)]
            pref = random.choice(group_size_options)
            students.append((email, hashed_pw, major, "student", pref, name))

        cursor.executemany("""
            INSERT INTO students (email, password_hash, major, role, group_size_pref, username)
            VALUES (?, ?, ?, ?, ?, ?)
        """, students)

        num_students = len(students)

        # =============================================
        # ENROLLMENTS
        # Realistic semester: every student in COP4710,
        # ~70% in COP3330 and CDA3100, plus 1-3 extras
        # =============================================
        random.seed(42)  # Reproducible results across runs
        enrollment_set = set()

        # All 120 students take COP4710 (course 1)
        for sid in range(1, num_students + 1):
            enrollment_set.add((sid, 1))

        # ~70% also take COP3330 (course 2) and CDA3100 (course 3)
        for sid in range(1, num_students + 1):
            if random.random() < 0.70:
                enrollment_set.add((sid, 2))
            if random.random() < 0.70:
                enrollment_set.add((sid, 3))

        # Each student picks 1-3 additional courses from the rest
        for sid in range(1, num_students + 1):
            extras = random.sample(range(4, 13), k=random.randint(1, 3))
            for cid in extras:
                enrollment_set.add((sid, cid))

        enrollments = list(enrollment_set)

        cursor.executemany("""
            INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)
        """, enrollments)

        # Build lookup: course_id -> list of enrolled student_ids
        enrolled_by_course = {}
        for sid, cid in enrollments:
            enrolled_by_course.setdefault(cid, []).append(sid)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # =============================================
        # STUDY GROUPS — 20 groups across courses (id 1-20)
        # =============================================
        study_groups = [
            # COP4710 - Databases (course 1): 5 groups
            (1, "SQL Squad",            now, 1),     # 1
            (1, "Normalization Nation",  now, 4),     # 2
            (1, "Join Masters",         now, 10),    # 3
            (1, "Query Crushers",       now, 15),    # 4
            (1, "Schema Stars",         now, 22),    # 5

            # COP3330 - OOP (course 2): 3 groups
            (2, "Polymorphism Pals",    now, 2),     # 6
            (2, "Inheritance Inc",      now, 8),     # 7
            (2, "OOP Overlords",        now, 30),    # 8

            # CDA3100 - Comp Org (course 3): 3 groups
            (3, "Binary Bandits",       now, 3),     # 9
            (3, "Register Rangers",     now, 12),    # 10
            (3, "MIPS Mavericks",       now, 25),    # 11

            # COP4610 - OS (course 4): 2 groups
            (4, "Kernel Crew",          now, 6),     # 12
            (4, "Deadlock Dodgers",     now, 18),    # 13

            # COP4530 - Data Structures (course 5): 2 groups
            (5, "Tree Traversers",      now, 5),     # 14
            (5, "Hash Heroes",          now, 20),    # 15

            # CEN4020 - Software Eng (course 6): 2 groups
            (6, "Agile Aces",           now, 11),    # 16
            (6, "Sprint Stars",         now, 35),    # 17

            # COP4020 - Prog Languages (course 7): 1 group
            (7, "Lambda Legends",       now, 40),    # 18

            # COT4420 - Theory of Comp (course 8): 1 group
            (8, "Turing Testers",       now, 50),    # 19

            # COP4531 - Complexity (course 12): 1 group
            (12, "Big-O Brigade",       now, 60),    # 20
        ]

        cursor.executemany("""
            INSERT INTO study_groups (course_id, name, created_at, leader_id)
            VALUES (?, ?, ?, ?)
        """, study_groups)

        # =============================================
        # GROUP MEMBERS
        # Leader + 2-5 additional members from enrolled students
        # =============================================
        group_info = {}
        for idx, (cid, _, _, lid) in enumerate(study_groups, start=1):
            group_info[idx] = (cid, lid)

        group_members = []
        assigned_to_group = {}

        for gid, (cid, leader_id) in group_info.items():
            pool = [s for s in enrolled_by_course.get(cid, []) if s != leader_id]
            extra_count = random.randint(2, 5)
            extras = random.sample(pool, k=min(extra_count, len(pool)))
            members = [leader_id] + extras

            assigned_to_group[gid] = set(members)
            for sid in members:
                group_members.append((gid, sid))

        cursor.executemany("""
            INSERT INTO group_members (group_id, student_id) VALUES (?, ?)
        """, group_members)

        # =============================================
        # APPOINTMENTS — 2-3 per group (~50 total)
        # Dates spread from last week through next 2 weeks
        # =============================================
        today = datetime.now()

        time_slots = [
            ("09:00", "10:00"), ("10:00", "11:30"), ("11:00", "12:00"),
            ("13:00", "14:00"), ("14:00", "15:30"), ("15:00", "16:30"),
            ("16:00", "17:30"), ("18:00", "19:30"),
        ]

        # Course-specific appointment titles
        titles_by_course = {
            1:  ["ER Diagram Review", "SQL Joins Practice", "Final Exam Prep",
                 "Normalization Workshop", "Relational Algebra Drill"],
            2:  ["Inheritance Deep Dive", "Polymorphism Practice", "Big Three Review",
                 "OOP Design Patterns", "C++ Debugging Session"],
            3:  ["MIPS Assembly Lab", "Datapath Walkthrough", "Binary Arithmetic Drill",
                 "Cache Memory Review", "Pipeline Hazards Study"],
            4:  ["Process Scheduling Lab", "Deadlock Practice", "Memory Management Review",
                 "Concurrency Problems", "File Systems Overview"],
            5:  ["BST Operations Review", "Graph Algorithm Practice", "Hash Table Deep Dive",
                 "Sorting Algorithm Race", "Complexity Analysis Review"],
            6:  ["Sprint Planning Review", "UML Diagram Session", "Requirements Workshop",
                 "Design Patterns Study", "Testing Strategy Review"],
            7:  ["Lambda Calculus Review", "Type Systems Study", "Functional Programming Lab"],
            8:  ["DFA/NFA Conversion", "Pumping Lemma Practice", "Turing Machine Workshop"],
            12: ["Amortized Analysis Study", "NP-Completeness Review", "Reduction Practice"],
        }

        course_title_map = {i + 1: courses[i][0] for i in range(len(courses))}

        appointments = []
        for gid, (cid, leader_id) in group_info.items():
            available_titles = titles_by_course.get(cid, ["Study Session", "Review Session", "Exam Prep"])
            num_appts = random.randint(2, 3)
            chosen_titles = random.sample(available_titles, k=min(num_appts, len(available_titles)))

            for title in chosen_titles:
                day_offset = random.randint(-5, 14)
                appt_date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                start_time, end_time = random.choice(time_slots)
                appt_leader = random.choice(list(assigned_to_group[gid]))
                description = f"{title} — {course_title_map.get(cid, 'Course')}"

                appointments.append((
                    title, start_time, end_time, appt_leader,
                    cid, gid, appt_date, description
                ))

        cursor.executemany("""
            INSERT INTO appointments (title, time, end_time, leader_id, course_id, group_id, date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, appointments)

        # =============================================
        # APPOINTMENT ATTENDEES
        # 2-5 members from the group attend each appointment
        # =============================================
        attendees = []
        for appt_idx, (_, _, _, _, _, gid, _, _) in enumerate(appointments, start=1):
            members_list = list(assigned_to_group[gid])
            num_attending = random.randint(2, min(5, len(members_list)))
            selected = random.sample(members_list, k=num_attending)
            for sid in selected:
                attendees.append((appt_idx, sid))

        cursor.executemany("""
            INSERT INTO appointment_attendees (appointment_id, student_id)
            VALUES (?, ?)
        """, attendees)

        conn.commit()

        # =============================================
        # PRINT SUMMARY
        # =============================================
        cursor.execute("SELECT COUNT(*) FROM students")
        s = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM courses")
        c = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM enrollments")
        e = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM study_groups")
        g = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM group_members")
        gm = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM appointments")
        a = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM appointment_attendees")
        aa = cursor.fetchone()[0]

        print(f"Seed complete:")
        print(f"  {s} students")
        print(f"  {c} courses")
        print(f"  {e} enrollments")
        print(f"  {g} study groups")
        print(f"  {gm} group memberships")
        print(f"  {a} appointments")
        print(f"  {aa} appointment attendees")

    except Exception as e:
        conn.rollback()
        print(f"Seed failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        cursor.close()
        conn.close()


def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")
