from db import get_db_connection
import sqlite3


def get_current_user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT
                id,
                email,
                major,
                role,
                group_size_pref,
                username
            FROM students
            WHERE id = ?
            """,
            (user_id,)
        )
        user = cursor.fetchone()
        return user

    finally:
        cursor.close()
        conn.close()


def update_current_user_profile(user_id, email, major, role, group_size_pref, username):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if not user_id:
            return False, "You must be logged in."

        if not email:
            return False, "Email is required."

        if not group_size_pref:
            return False, "Group size preference is required."
        
        if not username:
            return False, "Username preference is required."

        try:
            group_size_pref = int(group_size_pref)
        except ValueError:
            return False, "Group size preference must be a number."

        if group_size_pref <= 0:
            return False, "Group size preference must be greater than 0."

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE email = ? AND id != ?
            """,
            (email, user_id)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            return False, "That email is already in use."

        cursor.execute(
            """
            UPDATE students
            SET email = ?, major = ?, role = ?, group_size_pref = ?, username = ?
            WHERE id = ?
            """,
            (email, major, role, group_size_pref, username, user_id)
        )

        conn.commit()
        return True, "Profile updated successfully."

    except sqlite3.IntegrityError:
        conn.rollback()
        return False, "An error occurred while updating your profile."

    finally:
        cursor.close()
        conn.close()