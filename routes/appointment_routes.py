from flask import request, Blueprint, session, render_template, redirect, url_for, flash
from services.appointment_service import (
    create_appointment,
    get_group_appointments,
    leave_appointment,
    join_appointment
)
from services.group_service import get_my_groups, get_student_courses

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointments_bp.route("/", methods=["GET"])
def my_appointments_page():
    user_id = session.get("user_id")

    if not user_id:
        flash("You must be logged in to view your appointments.", "danger")
        return redirect(url_for("auth.login_endpoint"))

    search = request.args.get("search", "").strip()

    appointments = get_group_appointments(user_id, search)
    groups = get_my_groups(user_id)
    enrolled_courses = get_student_courses(user_id)

    return render_template(
        "appointments.html",
        appointments=appointments,
        groups=groups,
        enrolled_courses=enrolled_courses,
        search=search
    )


@appointments_bp.route("/create", methods=["POST"])
def create():
    appointment_name = request.form.get("appointment_name", "").strip()
    group_id = request.form.get("group_id", "").strip()
    time = request.form.get("time", "").strip()
    end_time = request.form.get("end_time", "").strip()

    success, message, appointment_id = create_appointment(
        appointment_name,
        time,
        end_time,
        group_id
    )

    flash(message, "success" if success else "danger")
    return redirect(url_for("appointments.my_appointments_page"))


@appointments_bp.route("/join", methods=["POST"])
def join():
    appointment_id = request.form.get("appointment_id", "").strip()
    user_id = session.get("user_id")

    success, message = join_appointment(appointment_id, user_id)

    flash(message, "success" if success else "danger")
    return redirect(url_for("appointments.my_appointments_page"))


@appointments_bp.route("/leave", methods=["POST"])
def leave():
    appointment_id = request.form.get("appointment_id", "").strip()
    user_id = session.get("user_id")

    success, message = leave_appointment(appointment_id, user_id)

    flash(message, "success" if success else "danger")
    return redirect(url_for("appointments.my_appointments_page"))