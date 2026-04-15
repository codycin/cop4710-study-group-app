# cop4710-study-group-app
Databases Study Group Application Project

A database-driven web application built for COP 4710 (Theory and Structure of Databases) at Florida State University. The app helps university students find, form, and manage study groups for their courses — replacing the friction of spamming GroupMe chats with intelligent, preference-based group discovery.

## Features

- **Account Registration & Profiles** — Students sign up with their email, major, and preferred study group size
- **Course Enrollment** — Add yourself to courses from the FSU catalog
- **Study Group Management** — Create, join, leave, and browse study groups filtered by course code
- **Auto-Match** — Algorithmically groups unassigned students in a course based on their group size preferences, handling edge cases like leftover students and overlapping constraints
- **Appointment Scheduling** — Schedule and manage study sessions tied to specific groups and courses
- **Group Roster** — View group members with a multi-table join across students, group members, and study groups

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite3 with raw SQL queries
- **Frontend:** Jinja2 templates, Bootstrap
- **Auth:** bcrypt password hashing

## Setup

```bash
git clone https://github.com/codycin/cop4710-study-group-app.git
cd cop4710-study-group-app
pip install -r requirements.txt
python app.py
```

The app runs at `http://localhost:5000`. Test data is seeded automatically on startup (120 students, 12 FSU courses). All test accounts use the password `password123`.
