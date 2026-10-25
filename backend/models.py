from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    age = Column(Integer, nullable=False)

    courses = relationship(
        "Course",
        back_populates="student",
        cascade="all, delete-orphan",
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)

    __table_args__ = (
        CheckConstraint("credits >= 1 AND credits <= 6", name="ck_course_credits"),
    )

    student = relationship("Student", back_populates="courses")
