from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas


def create_student(db: Session, data: schemas.StudentCreate):
    student = models.Student(**data.model_dump())
    db.add(student)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise
    return student


def get_students(db: Session, min_age=None):
    query = db.query(models.Student)
    if min_age is not None:
        query = query.filter(models.Student.age >= min_age)
    return query.all()


def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def update_student(db: Session, student_id: int, data: schemas.StudentUpdate):
    student = get_student(db, student_id)
    if student is None:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)

    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise
    return student


def delete_student(db: Session, student_id: int):
    student = get_student(db, student_id)
    if student is None:
        return False
    db.delete(student)
    db.commit()
    return True


def create_course(db: Session, data: schemas.CourseCreate):
    course = models.Course(**data.model_dump())
    db.add(course)
    try:
        db.commit()
        db.refresh(course)
    except IntegrityError:
        db.rollback()
        raise
    return course


def get_courses(db: Session):
    return db.query(models.Course).all()


def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def update_course(db: Session, course_id: int, data: schemas.CourseUpdate):
    course = get_course(db, course_id)
    if course is None:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(course, key, value)

    try:
        db.commit()
        db.refresh(course)
    except IntegrityError:
        db.rollback()
        raise
    return course


def delete_course(db: Session, course_id: int):
    course = get_course(db, course_id)
    if course is None:
        return False
    db.delete(course)
    db.commit()
    return True
