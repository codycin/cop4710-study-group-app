from flask import request, jsonify, Blueprint, session, render_template, redirect, url_for, flash
from services.auth_service import register, login

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET","POST"])
def register_endpoint():
    if request.method == "GET":
        return render_template("register.html")
    

    email = request.form.get("email")
    password = request.form.get("password")
    major = request.form.get("major")
    role = request.form.get("role")
    group_size_pref = request.form.get("groupSizePref")

    if not email or not password or not major or not role or group_size_pref is None:
        flash("Failed, missing fields","danger")
        return redirect(url_for("auth.register_endpoint"))

    try:
        group_size_pref = int(group_size_pref)
    except (TypeError, ValueError):
        flash("Failed, group size must be number")
        return redirect(url_for("auth.register_endpoint"))

    success, message, student_id = register(
        email=email,
        password=password,
        major=major,
        role=role,
        groupSizePref=group_size_pref
    )

    if not success:
        flash(message,"danger")
        return redirect(url_for("auth.register_endpoint"))
    
    session["user_id"] = student_id

    return redirect(url_for("courses"))

@auth_bp.route("/login", methods=["GET","POST"])
def login_endpoint():
    if request.method == "GET":
        return render_template("login.html")

    # POST
    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required", "danger")
        return redirect(url_for("auth.login_endpoint"))

    success, message, student_id = login(email, password)

    if not success:
        flash(message, "danger")
        return redirect(url_for("auth.login_endpoint"))

    session["user_id"] = student_id

    flash("Logged in successfully!", "success")
    return redirect(url_for("course.get_courses_page"))


