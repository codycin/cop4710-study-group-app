from collections import defaultdict
from db import get_db_connection
import sqlite3
from flask import session

def bucket_students_by_pref(students):
    buckets = defaultdict(list)
    for student in students:
        pref = student["group_size_pref"] or 3
        buckets[pref].append(student)
    return buckets