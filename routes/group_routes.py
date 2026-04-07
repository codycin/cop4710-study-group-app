from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.group_service import create_group, search_groups, join_group, get_student_courses, get_my_groups, leave_group

group_bp = Blueprint("groups", __name__, url_prefix="/groups")


@group_bp.route("/search", methods=["GET"])
def list_groups():
    user_id = session.get("user_id")
    course_code = request.args.get("course_code", "").strip()

    groups = search_groups(course_code)
    enrolled_courses = get_student_courses(user_id) if user_id else []

    return render_template(
        "groups.html",
        groups=groups,
        enrolled_courses=enrolled_courses
    )


@group_bp.route("/", methods=["POST"])
def join():
    user_id = session.get("user_id")
    group_id = request.form.get("group_id")

    success, message = join_group(user_id, group_id)
    flash(message)
    return redirect(url_for("groups.list_groups"))

@group_bp.route("/leave", methods=["POST"])
def leave():
    user_id = session.get("user_id")
    group_id = request.form.get("group_id")

    success, message = leave_group(user_id, group_id)
    flash(message)
    return redirect(url_for("groups.my_groups"))


@group_bp.route("/create", methods=["POST"])
def create():
    user_id = session.get("user_id")

    if not user_id:
        flash("You must be logged in to create a group.")
        return redirect(url_for("groups.list_groups"))

    group_name = request.form.get("group_name", "").strip()
    course_id = request.form.get("course_id", "").strip()

    success, message, group_id = create_group(course_id, group_name, user_id)
    flash(message)
    return redirect(url_for("groups.list_groups"))

@group_bp.route("/", methods=["GET"])
def my_groups():
    user_id = session.get("user_id")

    if not user_id:
        flash("You must be logged in to view your groups.")
        return redirect(url_for("groups.list_groups"))

    groups = get_my_groups(user_id)
    return render_template("my_groups.html", groups=groups)