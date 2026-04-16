from db import get_db_connection
import sqlite3
from flask import session


def create_appointment(title, time, end_time, group_id, date):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        student_id = session.get("user_id")
        if not student_id:
            return False, "You must be logged in to create an appointment.", None

        if not title or not time or not end_time or not group_id or not date:
            return False, "All fields are required.", None

        cursor.execute(
            "SELECT id, course_id FROM study_groups WHERE id = ?",
            (group_id,)
        )
        group = cursor.fetchone()

        if not group:
            return False, "Group not found.", None

        course_id = group["course_id"]

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
            return False, "You can only create appointments for groups you belong to.", None

        cursor.execute(
            """
            INSERT INTO appointments (title, time, end_time, leader_id, course_id, group_id, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, time, end_time, student_id, course_id, group_id, date)
        )
        appointment_id = cursor.lastrowid

        cursor.execute(
            """
            INSERT INTO appointment_attendees (appointment_id, student_id)
            VALUES (?, ?)
            """,
            (appointment_id, student_id)
        )

        conn.commit()
        return True, "Appointment created successfully.", appointment_id

    except sqlite3.IntegrityError:
        return False, "An error occurred while creating the appointment.", None

    finally:
        cursor.close()
        conn.close()


def get_group_appointments(student_id, search_term=""):
    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = (search_term or "").strip()

    query = """
        SELECT DISTINCT
            a.id,
            a.title,
            a.time,
            a.end_time,
            a.leader_id,
            a.course_id,
            a.group_id,
            a.date,
            sg.name AS group_name,
            c.code AS course_code,
            c.title AS course_title,
            (
                SELECT COUNT(*)
                FROM appointment_attendees aa2
                WHERE aa2.appointment_id = a.id
            ) AS member_count,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM appointment_attendees aa3
                    WHERE aa3.appointment_id = a.id
                      AND aa3.student_id = ?
                ) THEN 1
                ELSE 0
            END AS is_joined
        FROM appointments a
        JOIN study_groups sg ON a.group_id = sg.id
        JOIN courses c ON a.course_id = c.id
        JOIN group_members gm ON gm.group_id = a.group_id
        WHERE gm.student_id = ?
    """

    params = [student_id, student_id]

    if search_term:
        query += """
            AND (
                a.title LIKE ?
                OR sg.name LIKE ?
                OR c.code LIKE ?
                OR c.title LIKE ?
            )
        """
        like_value = f"%{search_term}%"
        params.extend([like_value, like_value, like_value, like_value])

    query += """
        ORDER BY a.time DESC, a.end_time DESC
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

def join_appointment(appointment_id, student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not student_id:
            return False, "You must be logged in to join an appointment."

        if not appointment_id:
            return False, "Appointment ID is required."

        cursor.execute(
            """
            SELECT id, title, group_id
            FROM appointments
            WHERE id = ?
            """,
            (appointment_id,)
        )
        appointment = cursor.fetchone()

        if not appointment:
            return False, "Appointment not found."

        cursor.execute(
            """
            SELECT 1
            FROM group_members
            WHERE group_id = ? AND student_id = ?
            """,
            (appointment["group_id"], student_id)
        )
        group_membership = cursor.fetchone()

        if not group_membership:
            return False, "You can only join appointments for groups you belong to."

        cursor.execute(
            """
            SELECT 1
            FROM appointment_attendees
            WHERE appointment_id = ? AND student_id = ?
            """,
            (appointment_id, student_id)
        )
        existing_membership = cursor.fetchone()

        if existing_membership:
            return False, "You have already joined this appointment."

        cursor.execute(
            """
            INSERT INTO appointment_attendees (appointment_id, student_id)
            VALUES (?, ?)
            """,
            (appointment_id, student_id)
        )

        conn.commit()
        return True, "You joined the appointment successfully."

    except sqlite3.IntegrityError:
        return False, "An error occurred while joining the appointment."

    finally:
        cursor.close()
        conn.close()
        
def leave_appointment(appointment_id, student_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not student_id:
            return False, "You must be logged in to leave a group."

        cursor.execute(
            "SELECT id, title, leader_id FROM appointments WHERE id = ?",
            (appointment_id,)
        )
        appointment = cursor.fetchone()

        if not appointment:
            return False, "Appointment not found."

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
            FROM appointment_attendees
            WHERE appointment_id = ? AND student_id = ?
            """,
            (appointment_id, student_id)
        )
        membership = cursor.fetchone()

        if not membership:
            return False, "You are not in this group."

        if(student_id == appointment["leader_id"]):
            return False, "Leader can only delete the appointment."



        cursor.execute(
            """
            DELETE FROM appointment_attendees
            WHERE appointment_id = ? AND student_id = ?
            """,
            (appointment_id, student_id)
        )

        conn.commit()
        return True, "You left the appointment."

    finally:
        cursor.close()
        conn.close()

def get_appointment_by_id(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT a.id, a.title, a.time, a.end_time, a.leader_id, a.course_id, a.group_id, a.date, a.description,
                   sg.name AS group_name, c.code AS course_code, c.title AS course_title
            FROM appointments a
            JOIN study_groups sg ON a.group_id = sg.id
            JOIN courses c ON a.course_id = c.id
            WHERE a.id = ?
            """,
            (appointment_id,)
        )
        appointment = cursor.fetchone()
        return appointment

    finally:
        cursor.close()
        conn.close()

def get_appointment_attendees(appointment_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT s.id, s.username, s.email
            FROM appointment_attendees aa
            JOIN students s ON aa.student_id = s.id
            WHERE aa.appointment_id = ?
            """,
            (appointment_id,)
        )
        attendees = cursor.fetchall()
        return attendees
    finally:
        cursor.close()
        conn.close()


def delete_appointment(appointment_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not user_id:
            return False, "You must be logged in to delete an appointment."

        cursor.execute(
            "SELECT id, leader_id FROM appointments WHERE id = ?",
            (appointment_id,)
        )
        appointment = cursor.fetchone()

        if not appointment:
            return False, "Appointment not found."

        if appointment["leader_id"] != user_id:
            return False, "Only the appointment leader can delete this appointment."

        # Delete attendees first (foreign key dependency)
        cursor.execute(
            "DELETE FROM appointment_attendees WHERE appointment_id = ?",
            (appointment_id,)
        )

        cursor.execute(
            "DELETE FROM appointments WHERE id = ?",
            (appointment_id,)
        )

        conn.commit()
        return True, "Appointment deleted successfully."

    except Exception:
        conn.rollback()
        return False, "An error occurred while deleting the appointment."

    finally:
        cursor.close()
        conn.close()

def get_my_appointments(student_id, search_term=""):
    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = (search_term or "").strip()

    query = """
        SELECT
            a.id,
            a.title,
            a.time,
            a.end_time,
            a.leader_id,
            a.course_id,
            a.group_id,
            a.date,
            sg.name AS group_name,
            c.code AS course_code,
            c.title AS course_title,

            -- total attendees
            (
                SELECT COUNT(*)
                FROM appointment_attendees aa2
                WHERE aa2.appointment_id = a.id
            ) AS member_count,

            -- always 1 now since we're filtering by joined
            1 AS is_joined

        FROM appointments a
        LEFT JOIN study_groups sg ON a.group_id = sg.id
        LEFT JOIN courses c ON a.course_id = c.id

        INNER JOIN appointment_attendees aa
            ON aa.appointment_id = a.id
           AND aa.student_id = ?
    """

    params = [student_id]

    if search_term:
        query += """
            WHERE (
                a.title LIKE ?
                OR sg.name LIKE ?
                OR c.code LIKE ?
                OR c.title LIKE ?
            )
        """
        like_value = f"%{search_term}%"
        params.extend([like_value, like_value, like_value, like_value])

    query += """
        ORDER BY a.date DESC, a.time DESC
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
