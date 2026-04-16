from flask import request, jsonify, Blueprint, render_template, session, template_rendered, redirect, url_for, flash
from services.course_service import createCourse
from db import get_db_connection


course_bp = Blueprint("course", __name__)

@course_bp.route("/createcourse", methods=["GET","POST"])
def create_course_endpoint():
    if request.method == "GET":
        return render_template("addcourse.html")
    
    title = request.form.get("title")
    code = request.form.get("code")

    if not title or not code:
        flash("Failed, missing fields","danger")
        return redirect(url_for("course.create_course_endpoint"))
    
    success, message, course_id = createCourse(
        title=title,
        code=code
    )

    if not success:
        flash(message,"danger")
        return redirect(url_for("course.create_course_endpoint"))

    flash(message, "success")
    return redirect (url_for("course.get_all_courses_page"))

@course_bp.route("/my-courses", methods=["GET"])

def get_courses_page():
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("auth.login_page"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.id, c.title, c.code
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.student_id = ?
        ORDER BY c.code
        """,
        (student_id,)
    )

    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("courses.html", courses=courses)

@course_bp.route("/courses", methods=["GET"])
def get_all_courses_page():
    conn = get_db_connection()
    cursor = conn.cursor()
    student_id = session.get("user_id")

    cursor.execute("""
        SELECT c.id, c.title, c.code
        FROM courses c
        WHERE NOT EXISTS (
            SELECT 1
            FROM enrollments e
            WHERE e.course_id = c.id
            AND e.student_id = ?
        )
        ORDER BY c.code
        """, (student_id,))
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("enroll.html", courses=courses)
    
    