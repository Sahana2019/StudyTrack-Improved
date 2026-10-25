from fastapi.testclient import TestClient

from backend.main import app


def test_students_list_and_min_age_filter():
    with TestClient(app) as client:
        response = client.get("/students/")
        assert response.status_code == 200
        assert len(response.json()) == 8

        filtered = client.get("/students/?min_age=20")
        assert filtered.status_code == 200
        assert all(item["age"] >= 20 for item in filtered.json())


def test_duplicate_email_is_client_error():
    with TestClient(app) as client:
        response = client.post(
            "/students/",
            json={"name": "Duplicate", "email": "aditi.rao@example.com", "age": 30},
        )
        assert response.status_code == 409


def test_invalid_email_is_validation_error():
    with TestClient(app) as client:
        response = client.post(
            "/students/",
            json={"name": "Invalid", "email": "invalid-email", "age": 30},
        )
        assert response.status_code == 422


def test_course_count_uses_seeded_enrollment():
    with TestClient(app) as client:
        response = client.get("/students/1/course-count")
        assert response.status_code == 200
        assert response.json()["course_count"] == 2


def test_algorithm_endpoints():
    with TestClient(app) as client:
        ages = client.get("/students/sorted?by=age").json()
        assert [s["age"] for s in ages] == [18, 19, 20, 21, 22, 23, 24, 25]

        search = client.get("/students/search?name=Priya%20Iyer")
        assert search.status_code == 200
        assert search.json()["name"] == "Priya Iyer"

        report = client.get("/students/report?min_age=21").json()
        assert report["count_meeting_min_age"] == 5


def test_ai_endpoints():
    with TestClient(app) as client:
        summary = client.post(
            "/assistant/summarize",
            json={"text": "Binary search works. It uses sorted data."},
        )
        assert summary.status_code == 200
        assert set(summary.json()) == {"topic", "key_points", "difficulty"}

        search = client.get("/assistant/search?query=binary%20search")
        assert search.status_code == 200
        assert search.json()["results"][0]["id"] == 1

        empty = client.get("/assistant/search?query=")
        assert empty.status_code == 200
        assert len(empty.json()["results"]) == 5
        assert all(item["score"] == 0.0 for item in empty.json()["results"])


def test_student_patch_and_delete():
    with TestClient(app) as client:
        created = client.post(
            "/students/",
            json={"name": "Temporary Student", "email": "temporary@example.com", "age": 28},
        )
        assert created.status_code == 201
        student_id = created.json()["id"]

        updated = client.patch(f"/students/{student_id}", json={"age": 29})
        assert updated.status_code == 200
        assert updated.json()["age"] == 29

        deleted = client.delete(f"/students/{student_id}")
        assert deleted.status_code == 204
        assert client.get(f"/students/{student_id}").status_code == 404


def test_course_crud_and_validation():
    with TestClient(app) as client:
        created = client.post(
            "/courses/",
            json={"course_name": "Testing", "credits": 4, "student_id": 1},
        )
        assert created.status_code == 201
        course_id = created.json()["id"]

        updated = client.patch(f"/courses/{course_id}", json={"credits": 5})
        assert updated.status_code == 200
        assert updated.json()["credits"] == 5

        invalid = client.post(
            "/courses/",
            json={"course_name": "Invalid", "credits": 7, "student_id": 1},
        )
        assert invalid.status_code == 422

        deleted = client.delete(f"/courses/{course_id}")
        assert deleted.status_code == 204


def test_missing_resources_return_404():
    with TestClient(app) as client:
        assert client.get("/students/999999").status_code == 404
        assert client.get("/courses/999999").status_code == 404
        assert client.get("/students/999999/course-count").status_code == 404
        assert client.get("/students/search?name=Nobody").status_code == 404


def test_cors_allows_documented_frontend_origin():
    with TestClient(app) as client:
        response = client.options(
            "/students/",
            headers={
                "Origin": "http://localhost:5500",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
