from flask import Flask, render_template
from routes.auth_routes import auth_bp
from db import create_tables
import sqlite3

app = Flask(__name__)

create_tables()

app.register_blueprint(auth_bp)


@app.route("/")
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)