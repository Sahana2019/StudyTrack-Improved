from backend.algorithms import (
    binary_search_by_name,
    count_students_meeting_min_age,
    format_roster_report,
    insertion_sort_by_field,
)


def roster():
    return [
        {"id": 1, "name": "Aditi Rao", "email": "a@x.com", "age": 22},
        {"id": 2, "name": "Farhan Sheikh", "email": "f@x.com", "age": 18},
        {"id": 3, "name": "Kavya Nair", "email": "k@x.com", "age": 25},
    ]


def test_insertion_sort_by_age_in_place():
    students = roster()
    original_id = id(students)
    result = insertion_sort_by_field(students, "age")
    assert id(result) == original_id
    assert [s["age"] for s in result] == [18, 22, 25]


def test_insertion_sort_by_name():
    students = roster()
    insertion_sort_by_field(students, "name")
    assert [s["name"] for s in students] == ["Aditi Rao", "Farhan Sheikh", "Kavya Nair"]


def test_binary_search_found_and_missing():
    students = sorted(roster(), key=lambda s: s["name"])
    assert binary_search_by_name(students, "Kavya Nair")["id"] == 3
    assert binary_search_by_name(students, "Nobody") == -1


def test_report_count_and_format():
    students = roster()
    assert count_students_meeting_min_age(students, 21) == 2
    assert format_roster_report(students).splitlines()[0] == "[Age 22] Aditi Rao <a@x.com>"
