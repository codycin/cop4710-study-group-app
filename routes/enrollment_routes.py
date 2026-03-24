from flask import request, jsonify, Blueprint, session, flash, redirect, url_for
from services.enrollment_service import enrollStudent, unenrollStudent

enrollment_bp = Blueprint("enrollment", __name__)

@enrollment_bp.route("/enrollstudent", methods=["POST"])
def enroll_student_endpoint():    
    user_id = session.get("user_id")

    course_id = request.form.get("course_id")

    if course_id is None:
      flash("Select course", "danger")
    
    success, message = enrollStudent(
        student_id=user_id,
        course_id=course_id
    )

    if not success:
        flash(message, "danger")
    else: flash(message, "success")

    return redirect(url_for("course.get_courses_page"))


@enrollment_bp.route("/unenrollstudent", methods=["POST"])
def unenroll_student_endpoint():
    student_id = session.get("user_id")
    course_id = request.form.get("course_id")

    success, message = unenrollStudent( student_id=student_id, course_id=course_id)

    if not success:
        flash(message, "danger")
    else: flash(message, "success")

    return redirect(url_for("course.get_courses_page"))

