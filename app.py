from flask import Flask, render_template
from routes.auth_routes import auth_bp
from routes.course_routes import course_bp
from routes.enrollment_routes import enrollment_bp
from routes.group_routes import group_bp


from db import create_tables

app = Flask(__name__)
app.secret_key = "thisisthesupersecretkey"

create_tables()

app.register_blueprint(auth_bp)
app.register_blueprint(course_bp)
app.register_blueprint(enrollment_bp)
app.register_blueprint(group_bp)

@app.route("/")
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)