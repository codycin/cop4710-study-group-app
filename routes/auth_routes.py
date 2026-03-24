from flask import Flask, request, jsonify, flash, redirect, url_for, Blueprint
from services.auth_service import register, login

app = Flask(__name__)

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register_endpoint():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body must be JSON"
        }), 400

    email = data.get("email")
    password = data.get("password")
    major = data.get("major")
    role = data.get("role")
    group_size_pref = data.get("groupSizePref")

    if not email or not password or not major or not role or group_size_pref is None:
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400

    try:
        group_size_pref = int(group_size_pref)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "groupSizePref must be an integer"
        }), 400

    success, message, student_id = register(
        email=email,
        password=password,
        major=major,
        role=role,
        groupSizePref=group_size_pref
    )

    if not success:
        return jsonify({
            "success": False,
            "message": message
        }), 400

    return jsonify({
        "success": True,
        "message": message,
        "studentId": student_id
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login_endpoint():
    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body must be JSON"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    success, message, student_id = login(email, password)

    status_code = 200 if success else 401

    return jsonify({
        "success": success,
        "message": message,
        "studentId": student_id
    }), status_code

