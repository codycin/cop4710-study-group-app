from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.group_service import search_groups, join_group

group_bp = Blueprint("groups", __name__,url_prefix="/groups")

@group_bp.route("/", methods=["GET"])
def list_groups():
    subject = request.args.get("subject", "").strip()
    course_number = request.args.get("course_number").strip()

    groups = search_groups(subject, course_number)
    return render_template("groups.html", groups=groups)

@group_bp.route("/", methods=["POST"])
def join():
    user_id = session.get("user_id")
    group_id = request.form.get("group_id")

    success, message = join_group(user_id, group_id)

    flash(message)
    return redirect(url_for("groups.list_groups"))