def insertion_sort_by_field(students, field):
    """Hand-written insertion sort; modifies students in place."""
    if field not in ("age", "name"):
        raise ValueError("field must be age or name")

    for i in range(1, len(students)):
        key_item = students[i]
        key_value = key_item[field]
        j = i - 1

        while j >= 0 and students[j][field] > key_value:
            students[j + 1] = students[j]
            j -= 1

        students[j + 1] = key_item

    return students


def binary_search_by_name(sorted_by_name_list, name):
    """Iterative binary search over a list already sorted by name."""
    low = 0
    high = len(sorted_by_name_list) - 1

    while low <= high:
        mid = low + (high - low) // 2
        current = sorted_by_name_list[mid]["name"]

        if current == name:
            return sorted_by_name_list[mid]
        if current < name:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def format_roster_report(students):
    lines = []
    for student in students:
        lines.append(f"[Age {student['age']}] {student['name']} <{student['email']}>")
    return "\n".join(lines)


def count_students_meeting_min_age(students, min_age):
    count = 0
    for student in students:
        if student["age"] >= min_age:
            count += 1
    return count
