from db import get_db_connection
import sqlite3
from datetime import datetime
from services.student_service import bucket_students_by_pref
from services.course_service import get_unassigned_students_for_course, get_course_by_id


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

        # Aggregate COUNT() query — enforce max group capacity
        # The max size is based on the group leader's group_size_pref
        cursor.execute(
            """
            SELECT MAX(s.group_size_pref) AS max_pref
            FROM group_members gm
            JOIN students s ON gm.student_id = s.id
            WHERE gm.group_id = ?
            """,
            (group_id,)
        )

        row = cursor.fetchone()
        max_size = row["max_pref"] if row and row["max_pref"] else 5

        cursor.execute(
            """
            SELECT COUNT(*) AS member_count
            FROM group_members
            WHERE group_id = ?
            """,
            (group_id,)
        )
        current_count = cursor.fetchone()["member_count"]

        if current_count >= max_size:
            return False, f"This group is full ({current_count}/{max_size} members)."

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
            "SELECT 1 FROM study_groups WHERE leader_id = ?",
            (student_id,)
        )
        leader = cursor.fetchone()
        if leader:
            return False, "You must transfer leadership before leaving the group."
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
            INSERT INTO study_groups (course_id, name, created_at, leader_id)
            VALUES (?, ?, ?, ?)
            """,
            (course_id, name, datetime.now().isoformat(), student_id)
        )
        
        group_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO group_members (group_id, student_id)
            VALUES (?, ?)
            """,
            (group_id, student_id)
        )

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

def get_group_by_id(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            sg.id,
            sg.name,
            sg.created_at,
            sg.leader_id,
            c.id AS course_id,
            c.code AS course_code,
            c.title AS course_title,
            s.username AS leader_username,
            s.email AS leader_email
        FROM study_groups sg
        JOIN courses c ON sg.course_id = c.id
        JOIN students s ON sg.leader_id = s.id
        WHERE sg.id = ?
        """,
        (group_id,)
    )

    group = cursor.fetchone()
    cursor.close()
    conn.close()
    return group

def get_group_appointments(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            a.id,
            a.title,
            a.date,
            a.time,
            a.end_time,
            a.leader_id,
            s.username AS leader_username
        FROM appointments a
        JOIN students s ON a.leader_id = s.id
        WHERE a.group_id = ?
        ORDER BY a.date, a.time
        """,
        (group_id,)
    )

    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return appointments

def get_group_members(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            s.id,
            s.username,
            s.email,
            s.major,
            s.group_size_pref
        FROM group_members gm
        JOIN students s ON gm.student_id = s.id
        WHERE gm.group_id = ?
        ORDER BY s.username
        """,
        (group_id,)
    )

    members = cursor.fetchall()
    cursor.close()
    conn.close()
    return members

def update_group_leader(group_id, new_leader_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE study_groups
        SET leader_id = ?
        WHERE id = ?
        """,
        (new_leader_id, group_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

def delete_group_by_id(group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments WHERE group_id = ?", (group_id,))
    cursor.execute("DELETE FROM group_members WHERE group_id = ?", (group_id,))
    cursor.execute("DELETE FROM study_groups WHERE id = ?", (group_id,))

    conn.commit()
    cursor.close()
    conn.close()

def is_group_member(group_id, student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM group_members
        WHERE group_id = ? AND student_id = ?
        """,
        (group_id, student_id)
    )

    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

def auto_match_students(students):
    buckets = bucket_students_by_pref(students)
    groups = []

    # First pass: exact groups
    for pref in sorted(buckets.keys()):
        bucket = buckets[pref]
        while len(bucket) >= pref:
            groups.append(bucket[:pref])
            del bucket[:pref]

    # Gather remaining students after exact matches
    unplaced = []
    for pref in sorted(buckets.keys()):
        unplaced.extend(buckets[pref])

    true_leftovers = []

    # Second pass: try to place remaining students into existing groups
    for student in unplaced:
        placed = False

        for group in groups:
            avg_pref = round(
                sum((member.get("group_size_pref") or 3) for member in group) / len(group)
            )

            # Allow group to grow up to its average preference, capped at 5
            max_size = min(max(avg_pref, 2), 5)

            if len(group) < max_size:
                group.append(student)
                placed = True
                break

        if not placed:
            true_leftovers.append(student)

    # Third pass: form new groups from leftovers if possible
    final_leftovers = []
    i = 0
    while i < len(true_leftovers):
        remaining = len(true_leftovers) - i

        if remaining >= 4:
            groups.append(true_leftovers[i:i+4])
            i += 4
        elif remaining >= 3:
            groups.append(true_leftovers[i:i+3])
            i += 3
        elif remaining >= 2:
            groups.append(true_leftovers[i:i+2])
            i += 2
        else:
            final_leftovers.extend(true_leftovers[i:])
            break

    return groups, final_leftovers

from datetime import datetime

def create_auto_matched_groups(course_id, created_by_user_id):
    students = get_unassigned_students_for_course(course_id)
    course = get_course_by_id(course_id)
    if len(students) < 2:
        return False, "Not enough unassigned students to form groups.", 0

    groups, leftovers = auto_match_students(students)

    if not groups:
        return False, "No valid groups could be formed.", 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        now = datetime.utcnow().isoformat(timespec="seconds")
        created_count = 0

        conn.execute("BEGIN")
        

        for index, group in enumerate(groups, start=1):
            leader_id = group[0]["id"]
            group_name = f"{course['code']} Group {index}"

            cursor.execute(
                """
                INSERT INTO study_groups (course_id, name, created_at, leader_id)
                VALUES (?, ?, ?, ?)
                """,
                (course_id, group_name, now, leader_id)
            )
            group_id = cursor.lastrowid

            for member in group:
                cursor.execute(
                    """
                    INSERT INTO group_members (group_id, student_id)
                    VALUES (?, ?)
                    """,
                    (group_id, member["id"])
                )
                    

            created_count += 1

        conn.commit()

        msg = f"Created {created_count} groups."
        if leftovers:
            msg += f" {len(leftovers)} student(s) could not be assigned."

        return True, msg, created_count

    except Exception as e:
        conn.rollback()
        print(students)
        print(type(students[0]))
        print(students[0])
        return False, f"Auto-match failed: {str(e)}", 0

    finally:
        cursor.close()
        conn.close()

def delete_all():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments")
    cursor.execute("DELETE FROM group_members")
    cursor.execute("DELETE FROM study_groups")

    conn.commit()
    cursor.close()
    conn.close()

from collections import Counter

def analyze_auto_matched_groups(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all groups for the course
        cursor.execute("""
            SELECT id, name, created_at, leader_id
            FROM study_groups
            WHERE course_id = ?
            ORDER BY id
        """, (course_id,))
        groups = cursor.fetchall()

        if not groups:
            return {
                "success": True,
                "course_id": course_id,
                "group_count": 0,
                "total_memberships": 0,
                "average_group_size": 0,
                "size_distribution": {},
                "duplicate_students": [],
                "groups_with_no_members": [],
                "groups_with_invalid_size": [],
                "groups_with_leader_not_in_group": [],
                "group_details": [],
                "summary": "No study groups found for this course."
            }

        group_details = []
        all_student_ids = []
        groups_with_no_members = []
        groups_with_invalid_size = []
        groups_with_leader_not_in_group = []

        for group in groups:
            group_id = group["id"]
            group_name = group["name"]
            leader_id = group["leader_id"]
            created_at = group["created_at"]

            cursor.execute("""
                SELECT student_id
                FROM group_members
                WHERE group_id = ?
                ORDER BY student_id
            """, (group_id,))
            members = cursor.fetchall()

            member_ids = [m["student_id"] for m in members]
            size = len(member_ids)

            all_student_ids.extend(member_ids)

            if size == 0:
                groups_with_no_members.append(group_id)

            # Based on your auto-match logic, final groups should be size 2–5
            if size < 2 or size > 5:
                groups_with_invalid_size.append({
                    "group_id": group_id,
                    "name": group_name,
                    "size": size
                })

            if leader_id not in member_ids:
                groups_with_leader_not_in_group.append({
                    "group_id": group_id,
                    "name": group_name,
                    "leader_id": leader_id
                })

            group_details.append({
                "group_id": group_id,
                "name": group_name,
                "created_at": created_at,
                "leader_id": leader_id,
                "member_ids": member_ids,
                "size": size
            })

        student_counts = Counter(all_student_ids)
        duplicate_students = [
            {"student_id": sid, "times_assigned": count}
            for sid, count in student_counts.items()
            if count > 1
        ]

        size_distribution = Counter(g["size"] for g in group_details)
        total_memberships = len(all_student_ids)
        group_count = len(group_details)
        average_group_size = total_memberships / group_count if group_count else 0

        return {
            "success": True,
            "course_id": course_id,
            "group_count": group_count,
            "total_memberships": total_memberships,
            "average_group_size": round(average_group_size, 2),
            "size_distribution": dict(sorted(size_distribution.items())),
            "duplicate_students": duplicate_students,
            "groups_with_no_members": groups_with_no_members,
            "groups_with_invalid_size": groups_with_invalid_size,
            "groups_with_leader_not_in_group": groups_with_leader_not_in_group,
            "group_details": group_details,
            "summary": (
                f"Found {group_count} groups with {total_memberships} total memberships. "
                f"Average size: {round(average_group_size, 2)}."
            )
        }

    except Exception as e:
        return {
            "success": False,
            "course_id": course_id,
            "error": str(e)
        }

    finally:
        cursor.close()
        conn.close()