from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentCreate(BaseModel):
    name: str
    email: str
    age: int = Field(gt=0)

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("email must contain @")
        return value


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0)

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, value):
        if value is not None and "@" not in value:
            raise ValueError("email must contain @")
        return value


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    age: int


class CourseCreate(BaseModel):
    course_name: str
    credits: int = Field(ge=1, le=6)
    student_id: int


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    credits: Optional[int] = Field(default=None, ge=1, le=6)
    student_id: Optional[int] = None


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_name: str
    credits: int
    student_id: int
