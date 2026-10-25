from . import models

SEED_STUDENTS = [
    {"name": "Aditi Rao", "email": "aditi.rao@example.com", "age": 22},
    {"name": "Rohan Mehta", "email": "rohan.mehta@example.com", "age": 19},
    {"name": "Kavya Nair", "email": "kavya.nair@example.com", "age": 25},
    {"name": "Farhan Sheikh", "email": "farhan.sheikh@example.com", "age": 18},
    {"name": "Priya Iyer", "email": "priya.iyer@example.com", "age": 21},
    {"name": "Devansh Gupta", "email": "devansh.gupta@example.com", "age": 23},
    {"name": "Meera Joshi", "email": "meera.joshi@example.com", "age": 20},
    {"name": "Sameer Khan", "email": "sameer.khan@example.com", "age": 24},
]

# The assignment specifies the exact student roster but does not prescribe
# course seed rows. These rows make the required course-count demo possible.
SEED_COURSES = [
    {"course_name": "Python Fundamentals", "credits": 4, "student_index": 0},
    {"course_name": "SQL Basics", "credits": 3, "student_index": 0},
    {"course_name": "FastAPI", "credits": 4, "student_index": 4},
]


def seed_if_empty(db):
    if db.query(models.Student).count() != 0:
        return

    students = [models.Student(**row) for row in SEED_STUDENTS]
    db.add_all(students)
    db.flush()

    for row in SEED_COURSES:
        db.add(
            models.Course(
                course_name=row["course_name"],
                credits=row["credits"],
                student_id=students[row["student_index"]].id,
            )
        )

    db.commit()
