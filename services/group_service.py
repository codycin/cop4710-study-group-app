from db import get_db_connection



def search_groups(subject, course_number):
    conn = get_db_connection()
    cursor = conn.cusor()

    query = """
        SELECT sg.id, c.subject_code, c.course_number, sg.max_size
        FROM study_group sg
        JOIN course c ON sg.course_id = c.id
        WHERE (? = '' OR c.subject_code = ?)
          AND (? = '' OR c.course_number = ?)
    """

    cursor.execute(query,(subject, subject, course_number, course_number))
    rows = cursor.fetchall()
    conn.close()

    return rows


def join_group(student_id, group_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS count FROM group_member WHERE group_id = ?", (group_id,))
    count_row = cursor.fetchone()
    current_count = count_row["count"]

    cursor.execute("SELECT max_size FROM study_group WHERE id = ?", (group_id,))
    group_row = cursor.fetchone()

    if not group_row:
        conn.close()
        return False, "Group not found."

    if current_count >= group_row["max_size"]:
        conn.close()
        return False, "This group is already full."

    cursor.execute(
        "INSERT INTO group_member (group_id, student_id) VALUES (?, ?)",
        (group_id, student_id)
    )
    conn.commit()
    conn.close()

    return True, "You joined the group."

