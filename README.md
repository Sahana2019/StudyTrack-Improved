# StudyTrack

StudyTrack is a single FastAPI + SQLite + SQLAlchemy application with a plain HTML/CSS/JavaScript dashboard. It combines:

1. Student/Course CRUD.
2. Hand-written Insertion Sort, Binary Search, and roster reporting.
3. An offline AI Helper with deterministic note summarization and fixed-vocabulary cosine-similarity search.

The project keeps the original assignment architecture and acceptance criteria intact while adding automated verification, clearer documentation, a test database configuration, and CI.

## Repository structure

```text
studytrack/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── algorithms.py
│   ├── ai_service.py
│   ├── seed_data.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_algorithms.py
│   └── test_ai_service.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── .env.example
├── .gitignore
└── README.md
```

## What was improved

### 1. Automated verification

The project now contains **21 automated tests** covering:
- API list/filter behavior.
- Student validation and duplicate-email handling.
- Student update/delete behavior.
- Course CRUD and credit validation.
- Missing-resource `404` responses.
- Database-backed course counts.
- Insertion Sort and Binary Search.
- Roster reporting.
- AI summarization determinism and edge cases.
- Exact 12-dimensional mock embeddings.
- Cosine-similarity zero-vector safety.
- Semantic-search ranking and empty-query behavior.
- CORS configuration.

The latest local verification completed with:

```text
21 passed, 0 warnings
```

The startup seeding logic uses FastAPI's lifespan API, so the local test run completes without framework deprecation warnings.

### 2. CI

GitHub Actions runs the test suite automatically on pushes and pull requests.

### 3. AI implementation corrected to the assignment specification

The mock embedding now uses exactly the required 12-word vocabulary and exact whole-token matching. Cosine similarity is calculated from first principles and safely returns `0.0` for a zero vector.

The summarizer:
- returns exactly `topic`, `key_points`, and `difficulty`;
- returns `topic="untitled"` and `key_points=[]` for empty/whitespace input;
- uses the documented first-non-empty-line topic rule;
- uses `<40` words = easy, `40–100` = medium, `>100` = hard.

The semantic-search endpoint accepts an empty query and returns all five notes with `0.0` scores in original ID order, as required by the acceptance criteria.

### 4. Database configuration for testing

The normal application still uses:

```text
sqlite:///./studytrack.db
```

The database URL can also be supplied through `STUDYTRACK_DATABASE_URL`, allowing automated tests to use an isolated SQLite database without touching the development database.

### 5. Database optimization review

The `Course.student_id` foreign key is indexed because it is used by the course-count aggregate and relationship lookups. No artificial benchmark claim is made: the assignment's eight-student demo dataset is too small to justify a meaningful performance percentage. The optimization is therefore limited to a sensible query-supporting index rather than an invented before/after metric.

### 6. Authentication decision

Authentication was **not added** to the submitted assignment build. The assignment does not define a user/account model, login flow, password policy, or authorization rules, and adding authentication would change the required demo flow for the single-user trainee dashboard. Rather than adding superficial authentication that is difficult to justify, this version prioritizes the graded CRUD, algorithms, AI Helper, testing, documentation, and CI requirements.

## Run the application

This solution uses **single-process mode**. FastAPI serves the frontend itself.

### Windows PowerShell

```powershell
cd studytrack
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000/
```

Swagger UI:

```text
http://localhost:8000/docs
```

The SQLite database is created automatically as `studytrack.db`. On first startup, the exact eight required students are inserted if the Student table is empty.

For local frontend development against a separate server, CORS explicitly permits `http://localhost:5500`. There is no wildcard `*` origin.

## Run the tests

From the repository root:

```powershell
pytest -q
```

The tests automatically use a separate SQLite database.

## Part 1 API

### Students

`POST /students/`

```json
{
  "name": "Test Student",
  "email": "test@example.com",
  "age": 22
}
```

Returns `201`.

`GET /students/`

Optional filter:

```text
/students/?min_age=20
```

Returns students whose age is at least the supplied value.

`GET /students/{student_id}`

Returns one student or `404`.

`PATCH /students/{student_id}`

Partial body, for example:

```json
{"age": 23}
```

`DELETE /students/{student_id}`

Returns `204` on success and `404` when the student does not exist.

### Courses

`POST /courses/`

```json
{
  "course_name": "Python",
  "credits": 4,
  "student_id": 1
}
```

`GET /courses/`

`GET /courses/{course_id}`

`PATCH /courses/{course_id}`

`DELETE /courses/{course_id}`

Course credits are constrained to 1 through 6 and `student_id` is a foreign key to Student.

### Course count

`GET /students/{student_id}/course-count`

The count is calculated in the database with SQLAlchemy `func.count`, rather than loading all Course rows and using Python `len()`.

### Validation

Student email validation rejects an email without `@` with a `422` validation response. Duplicate student email values are caught as a database integrity error and returned as `409`.

## Part 2 Algorithms

### Insertion Sort

`GET /students/sorted?by=age`

or:

```text
/students/sorted?by=name
```

`insertion_sort_by_field()` is a hand-written in-place Insertion Sort. It starts from the second element, shifts larger values with a visible `while` loop, and inserts the key. It does not call `sort()` or `sorted()`.

Worst-case time is `O(n²)` because reverse-ordered data can require each new element to move across most of the sorted prefix. Best-case time is `O(n)` because already-sorted data causes only one comparison per element before the shifting loop stops. Extra space is `O(1)` apart from the input list because the algorithm sorts in place.

### Binary Search

`GET /students/search?name=Priya%20Iyer`

The endpoint first creates a name-sorted copy with Python's `sorted()`. The actual `binary_search_by_name()` implementation is iterative and uses:

```text
mid = low + (high - low) // 2
```

Binary Search requires the list to be sorted by the same field being searched because the midpoint comparison determines which half can be safely discarded. Without that ordering, the algorithm cannot know which side contains the target.

### Report

`GET /students/report?min_age=21`

Returns:

```json
{
  "report": "[Age 22] Aditi Rao <aditi.rao@example.com>\n...",
  "count_meeting_min_age": 5
}
```

## Part 3 AI Helper

The implementation uses **offline mock mode** for grading. No network request or API key is required.

### Summarizer

`POST /assistant/summarize`

Body:

```json
{
  "text": "Binary search works on sorted data. It repeatedly halves the range."
}
```

Returns exactly:

```json
{
  "topic": "...",
  "key_points": ["...", "..."],
  "difficulty": "easy"
}
```

Rules:
- Topic: first non-empty line, with punctuation removed. If there is no usable topic, the fallback is `"untitled"`.
- Key points: up to the first three non-empty sentences split on `.`, `!`, or `?`.
- Difficulty: fewer than 40 words = easy; 40–100 = medium; more than 100 = hard.

The route also accepts the original project's `raw_text` field for backward compatibility, but `text` is the documented assignment payload.

### Real-LLM prompt documented for future use

If a real provider were added, the prompt would be:

```text
Task: Summarize the user's study notes.

Context:
The notes may contain technical or educational material. Identify the main topic and extract the most useful points without inventing information.

Constraints:
1. Use only information supported by the supplied notes.
2. key_points must contain up to 3 concise points.
3. difficulty must be exactly one of: "easy", "medium", "hard".
4. Return valid JSON.
5. Return exactly these three keys and no additional keys: topic, key_points, difficulty.
6. If the notes are empty, return topic "untitled", key_points [], and difficulty "easy".

Format:
{
  "topic": "string",
  "key_points": ["string"],
  "difficulty": "easy | medium | hard"
}
```

### Semantic search

`GET /assistant/search?query=binary%20search`

The implementation uses the required five notes and this exact 12-word vocabulary:

```text
sort, search, binary, insertion, sql, join,
fastapi, pydantic, prompt, llm, database, validate
```

Tokenization lower-cases the text and splits on every run of non-letter/non-digit characters. Only exact whole-token matches count.

`mock_embed()` always returns exactly 12 numbers.

`cosine_similarity()` implements:

```text
dot_product / (magnitude_a * magnitude_b)
```

from first principles. If either vector has zero magnitude, it returns `0.0` without dividing by zero.

An empty or out-of-vocabulary search query succeeds and returns all five notes with `0.0` scores in their original ID order.

For:

```text
GET /assistant/search?query=binary%20search
```

note `1` ranks first.

## Exact seeded students

- Aditi Rao — aditi.rao@example.com — 22
- Rohan Mehta — rohan.mehta@example.com — 19
- Kavya Nair — kavya.nair@example.com — 25
- Farhan Sheikh — farhan.sheikh@example.com — 18
- Priya Iyer — priya.iyer@example.com — 21
- Devansh Gupta — devansh.gupta@example.com — 23
- Meera Joshi — meera.joshi@example.com — 20
- Sameer Khan — sameer.khan@example.com — 24

Therefore:

```text
GET /students/sorted?by=age
```

returns:

```text
Farhan Sheikh 18
Rohan Mehta 19
Meera Joshi 20
Priya Iyer 21
Aditi Rao 22
Devansh Gupta 23
Sameer Khan 24
Kavya Nair 25
```

And:

```text
GET /students/report?min_age=21
```

has:

```text
count_meeting_min_age = 5
```

## Frontend verification

The dashboard:
- loads the roster from this backend using `fetch("/students/")`;
- creates cards using `document.createElement()` and `appendChild()`;
- has visible padding, margin and borders;
- switches to one column below 600px;
- uses one event listener on `#roster-list` for Save Age/Delete through event delegation;
- uses PATCH for age changes;
- uses DELETE for student deletion;
- uses POST for adding students without a page reload;
- displays a visible `#error-banner` for failed requests;
- exposes the algorithm features;
- exposes the AI Helper summarizer and semantic search.

## CI/CD

The repository contains `.github/workflows/tests.yml`. It installs the backend requirements and runs:

```text
pytest -q
```

on pushes and pull requests.

This is CI verification rather than a deployment pipeline. No deployment service was added because the assignment does not require hosting and there is no need to claim a deployment that was not actually performed.

## Git workflow requirement

The ZIP archive does not contain Git history. After extracting it into your Git repository, create the required feature branch and merge history:

```powershell
git init
git add .
git commit -m "Initial StudyTrack structure"

git checkout -b feature/studytrack-quality
git add backend frontend tests
git commit -m "Improve AI engine and add automated tests"

git add .
git commit -m "Document verification and CI workflow"

git checkout main
git merge --no-ff feature/studytrack-quality -m "Merge StudyTrack quality improvements"

git log --graph --oneline --all
```

The final public repository should contain the full application and this branch/merge history.

## Resume-ready project evidence

After this update, accurate measurable statements include:

- Built a FastAPI + SQLAlchemy + SQLite study-management application with Student/Course CRUD, algorithm endpoints, and an integrated offline AI Helper.
- Implemented hand-written Insertion Sort and iterative Binary Search as callable API features, plus a database-backed course-count aggregate.
- Added **21 automated unit/integration tests** covering validation, CRUD behavior, algorithms, AI edge cases, database operations, and CORS.
- Added GitHub Actions CI to execute the automated test suite on pushes and pull requests.
- Implemented a deterministic 12-dimensional fixed-vocabulary embedding and first-principles cosine similarity with zero-vector handling.

These statements describe work present in the repository and do not claim production deployment, real-LLM API usage, or authentication that was not implemented.
