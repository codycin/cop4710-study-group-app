from flask import Flask, render_template, session
from routes.auth_routes import auth_bp
from routes.course_routes import course_bp
from routes.enrollment_routes import enrollment_bp
from routes.group_routes import group_bp
from routes.appointment_routes import appointments_bp
from services.auth_service import get_user_by_id
from seed import seed_test_data
from routes.profile_routes import profile_bp
from datetime import datetime
from db import create_tables

app = Flask(__name__)
app.secret_key = "thisisthesupersecretkey"

create_tables()
seed_test_data()


app.register_blueprint(auth_bp)
app.register_blueprint(course_bp)
app.register_blueprint(enrollment_bp)
app.register_blueprint(group_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(profile_bp)


@app.route("/")
def index():
    return render_template("index.html")

@app.context_processor
def inject_user():
    user_id = session.get("user_id")
    user = None
    if user_id:
        user = get_user_by_id(user_id)  

    return dict(current_user=user)

@app.template_filter('format_date')
def format_date(value):
    dt = datetime.strptime(value, "%Y-%m-%d")
    return dt.strftime("%b %d")  # Apr 09

@app.template_filter('format_time')
def format_time(value):
    dt = datetime.strptime(value, "%H:%M")
    return dt.strftime("%I:%M %p")  # 02:30 PM

if __name__ == "__main__":
    app.run(debug=True)