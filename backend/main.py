from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import algorithms, ai_service, crud, models, schemas
from .database import Base, engine, get_db
from .seed_data import seed_if_empty

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db = next(get_db())
    try:
        seed_if_empty(db)
        yield
    finally:
        db.close()


app = FastAPI(title="StudyTrack API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/students/", response_model=schemas.StudentRead, status_code=201)
def create_student(data: schemas.StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, data)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")


@app.get("/students/", response_model=list[schemas.StudentRead])
def list_students(
    min_age: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
):
    return crud.get_students(db, min_age=min_age)


@app.get("/students/sorted", response_model=list[schemas.StudentRead])
def sorted_students(
    by: str = Query(default="age", pattern="^(age|name)$"),
    db: Session = Depends(get_db),
):
    students = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age}
        for s in crud.get_students(db)
    ]
    algorithms.insertion_sort_by_field(students, by)
    return students


@app.get("/students/search", response_model=schemas.StudentRead)
def search_student(name: str, db: Session = Depends(get_db)):
    students = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age}
        for s in crud.get_students(db)
    ]
    name_sorted = sorted(students, key=lambda student: student["name"])
    result = algorithms.binary_search_by_name(name_sorted, name)

    if result == -1:
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@app.get("/students/report")
def student_report(min_age: int = Query(default=21, gt=0), db: Session = Depends(get_db)):
    students = [
        {"id": s.id, "name": s.name, "email": s.email, "age": s.age}
        for s in crud.get_students(db)
    ]
    return {
        "report": algorithms.format_roster_report(students),
        "count_meeting_min_age": algorithms.count_students_meeting_min_age(
            students, min_age
        ),
    }


@app.get("/students/{student_id}/course-count")
def student_course_count(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    count = (
        db.query(func.count(models.Course.id))
        .filter(models.Course.student_id == student_id)
        .scalar()
    )

    return {"student_id": student_id, "course_count": count}


@app.get("/students/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.patch("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(
    student_id: int,
    data: schemas.StudentUpdate,
    db: Session = Depends(get_db),
):
    try:
        student = crud.update_student(db, student_id, data)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    if not crud.delete_student(db, student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return None


@app.post("/courses/", response_model=schemas.CourseRead, status_code=201)
def create_course(data: schemas.CourseCreate, db: Session = Depends(get_db)):
    if crud.get_student(db, data.student_id) is None:
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        return crud.create_course(db, data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid course data")


@app.get("/courses/", response_model=list[schemas.CourseRead])
def list_courses(db: Session = Depends(get_db)):
    return crud.get_courses(db)


@app.get("/courses/{course_id}", response_model=schemas.CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course(db, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@app.patch("/courses/{course_id}", response_model=schemas.CourseRead)
def update_course(
    course_id: int,
    data: schemas.CourseUpdate,
    db: Session = Depends(get_db),
):
    if data.student_id is not None and crud.get_student(db, data.student_id) is None:
        raise HTTPException(status_code=404, detail="Student not found")

    try:
        course = crud.update_course(db, course_id, data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid course data")

    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@app.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    if not crud.delete_course(db, course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    return None


@app.post("/assistant/summarize")
def assistant_summarize(payload: dict):
    raw_text = payload.get("text")
    if raw_text is None:
        # Backward-compatible with the original project payload.
        raw_text = payload.get("raw_text")
    if not isinstance(raw_text, str):
        raise HTTPException(status_code=422, detail="text must be a string")
    return ai_service.summarize_notes(raw_text)


@app.get("/assistant/search")
def assistant_search(
    query: str = "",
    limit: int = Query(default=5, ge=1, le=5),
):
    return {"query": query, "results": ai_service.semantic_search(query, limit)}


# Keep API routes above the static mount. Single-process mode:
# http://localhost:8000/ serves frontend/index.html.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
