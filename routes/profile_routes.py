from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from services.profile_service import get_current_user_profile, update_current_user_profile

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET"])
def view_profile():
    user_id = session.get("user_id")

    if not user_id:
        flash("You must be logged in to view your profile.", "danger")
        return redirect(url_for("auth.login_endpoint"))

    user = get_current_user_profile(user_id)

    if not user:
        flash("Profile not found.", "danger")
        return redirect(url_for("index"))

    return render_template("profile.html", user=user)


@profile_bp.route("/edit", methods=["GET", "POST"])
def edit_profile():
    user_id = session.get("user_id")

    if not user_id:
        flash("You must be logged in to edit your profile.", "danger")
        return redirect(url_for("auth.login_endpoint"))

    if request.method == "GET":
        user = get_current_user_profile(user_id)

        if not user:
            flash("Profile not found.", "danger")
            return redirect(url_for("index"))

        return render_template("edit_profile.html", user=user)

    email = (request.form.get("email") or "").strip()
    major = (request.form.get("major") or "").strip()
    role = (request.form.get("role") or "").strip()
    group_size_pref = (request.form.get("group_size_pref") or "").strip()
    username = (request.form.get("username") or "").strip()

    success, message = update_current_user_profile(
        user_id=user_id,
        email=email,
        major=major,
        role=role,
        group_size_pref=group_size_pref,
        username=username
    )

    flash(message, "success" if success else "danger")

    if success:
        return redirect(url_for("profile.view_profile"))

    user = get_current_user_profile(user_id)
    return render_template("edit_profile.html", user=user)