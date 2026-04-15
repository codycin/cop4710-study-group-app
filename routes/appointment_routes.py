from datetime import datetime, timedelta

from flask import request, Blueprint, session, render_template, redirect, url_for, flash
from services.appointment_service import (
    create_appointment,
    get_appointment_attendees,
    get_appointment_by_id,
    get_group_appointments,
    leave_appointment,
    join_appointment,
    delete_appointment,
    get_my_appointments
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
    selected_group_id = request.args.get("group_id", type=int)  

    appointments = get_group_appointments(user_id, search)
    groups = get_my_groups(user_id)
    enrolled_courses = get_student_courses(user_id)

    return render_template(
        "appointments.html",
        appointments=appointments,
        groups=groups,
        enrolled_courses=enrolled_courses,
        search=search,
        selected_group_id=selected_group_id  
    )

@appointments_bp.route("/my", methods=["GET"])
def my_appointments():
    student_id = session.get("user_id")

    if not student_id:
        flash("You must be logged in to view your appointments.", "danger")
        return redirect(url_for("auth.login_endpoint"))

    search_term = request.args.get("search", "").strip()
    appointments = get_my_appointments(student_id, search_term)

    return render_template(
        "my_appointments.html",
        appointments=appointments,
        search_term=search_term
    )


@appointments_bp.route("/create", methods=["POST"])
def create():
    appointment_name = request.form.get("appointment_name", "").strip()
    group_id = request.form.get("group_id", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    hours = request.form.get("hours", "").strip()
    minutes = request.form.get("minutes", "").strip()


    hours = int(hours) if hours else 0
    minutes = int(minutes) if minutes else 0

    start_dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + timedelta(hours=hours, minutes=minutes)

    end_time = end_dt.strftime("%H:%M")

    success, message, appointment_id = create_appointment(
        appointment_name,
        time,
        end_time,
        group_id,
        date
    )

    flash(message, "success" if success else "danger")
    return redirect(url_for("appointments.my_appointments_page"))


@appointments_bp.route("/join", methods=["POST"])
def join():
    appointment_id = request.form.get("appointment_id", "").strip()
    user_id = session.get("user_id")

    success, message = join_appointment(appointment_id, user_id)

    flash(message, "success" if success else "danger")
    return redirect(url_for("appointments.view", appointment_id=appointment_id))


@appointments_bp.route("/leave", methods=["POST"])
def leave():
    appointment_id = request.form.get("appointment_id", "").strip()
    user_id = session.get("user_id")

    success, message = leave_appointment(appointment_id, user_id)

    flash(message, "success" if success else "danger")
    return redirect(url_for("appointments.my_appointments_page"))

@appointments_bp.route("/<int:appointment_id>")
def view(appointment_id):
    user_id = session.get("user_id")

    if not user_id:
        flash("You must be logged in to view appointment details.", "danger")
        return redirect(url_for("auth.login_endpoint"))

    appointment = get_appointment_by_id(appointment_id)
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for("appointments.my_appointments_page"))

    members = get_appointment_attendees(appointment_id)
    is_appointment_leader = user_id == appointment["leader_id"]

    return render_template(
        "appointment_detail.html",
        appointment=appointment,
        members=members,
        current_user_id=user_id,
        is_appointment_leader=is_appointment_leader,
        is_joined=user_id in [m["id"] for m in members]
    )


@appointments_bp.route("/delete", methods=["POST"])
def delete():
    appointment_id = request.form.get("appointment_id", "").strip()
    user_id = session.get("user_id")

    success, message = delete_appointment(appointment_id, user_id)

    flash(message, "success" if success else "danger")
    return redirect(url_for("appointments.my_appointments_page"))