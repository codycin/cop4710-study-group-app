from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.group_service import analyze_auto_matched_groups, create_auto_matched_groups, create_group, delete_all, is_group_member, search_groups, join_group, get_student_courses, get_my_groups, leave_group, get_group_by_id, get_group_members, get_group_appointments, update_group_leader, delete_group_by_id 

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
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for("groups.list_groups"))

@group_bp.route("/leave", methods=["POST"])
def leave():
    user_id = session.get("user_id")
    group_id = request.form.get("group_id")

    success, message = leave_group(user_id, group_id)

    if success:
        flash(message, "success")
        return redirect(url_for("groups.my_groups"))

    else:
        flash(message, "danger")
        return redirect(url_for("groups.view", group_id=group_id))


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

@group_bp.route("/groups/<int:group_id>")
def view(group_id):
    user_id = session.get("user_id")
    group = get_group_by_id(group_id)
    if not group:
        flash("Group not found.", "danger")
        return redirect(url_for("groups.index"))

    members = get_group_members(group_id)
    appointments = get_group_appointments(group_id)
    is_group_leader = user_id == group["leader_id"]

    return render_template(
        "group_detail.html",
        group=group,
        members=members,
        appointments=appointments,
        current_user_id=user_id,
        is_group_leader=is_group_leader
    )

@group_bp.route("/groups/transfer-ownership", methods=["POST"])
def transfer_ownership():
    current_user_id = session.get("user_id")
    group_id = request.form.get("group_id", type=int)
    new_leader_id = request.form.get("new_leader_id", type=int)

    group = get_group_by_id(group_id)
    if not group:
        flash("Group not found.", "danger")
        return redirect(url_for("groups.index"))

    if group["leader_id"] != current_user_id:
        flash("Only the group leader can transfer ownership.", "danger")
        return redirect(url_for("groups.view", group_id=group_id))
    
    if not is_group_member(group_id, new_leader_id):
        flash("Selected user is not a member of this group.", "danger")
        return redirect(url_for("groups.view", group_id=group_id))

    update_group_leader(group_id, new_leader_id)

    flash("Group ownership transferred successfully.", "success")
    return redirect(url_for("groups.view", group_id=group_id))

@group_bp.route("/groups/delete", methods=["POST"])
def delete_group():
    current_user_id = session.get("student_id")
    group_id = request.form.get("group_id", type=int)

    group = get_group_by_id(group_id)
    if not group:
        flash("Group not found.", "danger")
        return redirect(url_for("groups.index"))

    if group["leader_id"] != current_user_id:
        flash("Only the group leader can delete the group.", "danger")
        return redirect(url_for("groups.view", group_id=group_id))

    delete_group_by_id(group_id)

    flash("Group deleted successfully.", "success")
    return redirect(url_for("groups.index"))

@group_bp.route("/auto-match", methods=["POST"])
def auto_match():
    user_id = session.get("user_id")
    course_id = request.form.get("course_id", type=int)

    if not user_id:
        flash("You must be logged in.", "danger")
        return redirect(url_for("auth.login_endpoint"))

    if not course_id:
        flash("Course is required.", "danger")
        return redirect(url_for("groups.list_groups"))

    success, message, created_count = create_auto_matched_groups(course_id, user_id)
    flash(message, "success" if success else "danger")

    return redirect(url_for("groups.list_groups", course_id=course_id))

@group_bp.route("/deleteall", methods=["POST"])
def delete_all_groups():
    delete_all()
    flash("All groups deleted successfully.", "success")
    return redirect(url_for("groups.list_groups"))


@group_bp.route("/analyze/<int:course_id>", methods=["GET"])
def analyze_groups_page(course_id):
    analysis = analyze_auto_matched_groups(course_id)
    return render_template("analyze.html", analysis=analysis, course_id=course_id)



