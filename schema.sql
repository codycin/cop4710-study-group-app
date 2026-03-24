DROP TABLE IF EXISTS students;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    major TEXT,
    role TEXT,
    group_size_pref INTEGER NOT NULL
);