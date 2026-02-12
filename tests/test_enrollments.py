from fastapi.testclient import TestClient
from main import app
from app.crud.enrollments import get_all_enrollments
from app.in_memory_db import DB
from app.schemas.user import UserRole
from app.dependencies import require_admin_role, require_student_role, get_current_user_role
import pytest
from uuid import UUID

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    DB["users"].clear()
    DB["courses"].clear()
    DB["enrollments"].clear()
    app.dependency_overrides = {}
    yield
    DB["users"].clear()
    DB["courses"].clear()
    DB["enrollments"].clear()
    app.dependency_overrides = {}

# Helper to create a student user and return its ID
def create_student_user(email="philip@example.com"):
    response = client.post(
        "/users/",
        json={"name": "Philip Onyema", "email": email, "role": "student"}
    )
    assert response.status_code == 201
    return response.json()["id"]

# Helper to create a course (needs admin override) and return its ID
def create_course(title, code):
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    response = client.post(
        "/courses/",
        json={"title": title, "code": code}
    )
    assert response.status_code == 201
    course_id = response.json()["id"]
    app.dependency_overrides.pop(require_admin_role, None)
    return course_id

# Helper to enroll a student (needs student override)
def enroll_student(student_id, course_id):
    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    response = client.post(
        "/enrollments/",
        json={"user_id": student_id, "course_id": course_id}
    )
    app.dependency_overrides.pop(require_student_role, None)
    return response

# --- Student Access Tests ---
def test_enroll_student_in_course_success():
    student_id = create_student_user()
    course_id = create_course("Backend Python", "BEP101")

    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    response = client.post(
        "/enrollments/",
        json={"user_id": student_id, "course_id": course_id}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == student_id
    assert data["course_id"] == course_id
    assert "id" in data
    assert len(get_all_enrollments()) == 1

def test_enroll_student_not_student_fails():
    # Create an admin user and try to enroll them - should fail
    admin_response = client.post(
        "/users/",
        json={"name": "Mr Rotimi", "email": "rotimi@altschool.com", "role": "admin"}
    )
    admin_id = admin_response.json()["id"]
    course_id = create_course("Frontend JavaScript", "FEJ201")

    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    response = client.post(
        "/enrollments/",
        json={"user_id": admin_id, "course_id": course_id}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found or not a student"

def test_enroll_course_not_found_fails():
    student_id = create_student_user()
    non_existent_course_id = "12345678-1234-5678-1234-567812345678"

    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    response = client.post(
        "/enrollments/",
        json={"user_id": student_id, "course_id": non_existent_course_id}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"

def test_enroll_already_enrolled_fails():
    student_id = create_student_user()
    course_id = create_course("Backend Node JS", "BEN101")

    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    client.post("/enrollments/", json={"user_id": student_id, "course_id": course_id})
    response = client.post(
        "/enrollments/",
        json={"user_id": student_id, "course_id": course_id}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already enrolled in this course"

def test_deregister_student_from_course_success():
    student_id = create_student_user()
    course_id = create_course("Database Management", "DBM101")

    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    post_response = client.post("/enrollments/", json={"user_id": student_id, "course_id": course_id})
    enrollment_id = post_response.json()["id"]

    response = client.delete(f"/enrollments/{enrollment_id}")
    assert response.status_code == 204
    assert len(get_all_enrollments()) == 0

def test_deregister_non_existent_enrollment_fails():
    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    non_existent_enrollment_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.delete(f"/enrollments/{non_existent_enrollment_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Enrollment not found"

def test_get_enrollments_for_specific_student_success():
    student_id = create_student_user()
    course_id_1 = create_course("Frontend HTML CSS", "FEH101")
    course_id_2 = create_course("Git and Version Control", "GVC101")

    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    client.post("/enrollments/", json={"user_id": student_id, "course_id": course_id_1})
    client.post("/enrollments/", json={"user_id": student_id, "course_id": course_id_2})

    response = client.get(f"/enrollments/users/{student_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(e["course_id"] == course_id_1 for e in data)
    assert any(e["course_id"] == course_id_2 for e in data)

def test_get_enrollments_for_non_existent_student_fails():
    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    non_existent_student_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.get(f"/enrollments/users/{non_existent_student_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found or not a student"

def test_student_tries_to_access_admin_endpoint_fails():
    # Student should not be able to view all enrollments (admin only)
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.student
    response = client.get("/enrollments/")
    assert response.status_code == 403
    assert response.json()["detail"] == "Nahh!!, You must be an Admin to get this working."

# --- Admin Oversight Tests ---
def test_get_all_enrollments_as_admin_success():
    student_id_1 = create_student_user("philip@example.com")
    student_id_2 = create_student_user("chioma@example.com")
    course_id_1 = create_course("Backend Python", "BEP101")
    course_id_2 = create_course("Frontend React", "FER201")
    course_id_3 = create_course("DevOps Basics", "DOP101")

    # Enroll students
    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    client.post("/enrollments/", json={"user_id": student_id_1, "course_id": course_id_1})
    client.post("/enrollments/", json={"user_id": student_id_1, "course_id": course_id_2})
    client.post("/enrollments/", json={"user_id": student_id_2, "course_id": course_id_3})
    app.dependency_overrides = {}

    # Now query as admin
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    response = client.get("/enrollments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_get_enrollments_for_specific_course_as_admin_success():
    student_id_1 = create_student_user("philip@example.com")
    student_id_2 = create_student_user("tunde@example.com")
    course_id_1 = create_course("Backend Node JS", "BEN101")
    course_id_2 = create_course("Cloud Computing", "CLD201")

    # Enroll students
    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    client.post("/enrollments/", json={"user_id": student_id_1, "course_id": course_id_1})
    client.post("/enrollments/", json={"user_id": student_id_2, "course_id": course_id_1})
    client.post("/enrollments/", json={"user_id": student_id_1, "course_id": course_id_2})
    app.dependency_overrides = {}

    # Query as admin
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    response = client.get(f"/enrollments/courses/{course_id_1}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(e["course_id"] == course_id_1 for e in data)

def test_get_enrollments_for_non_existent_course_as_admin_fails():
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    non_existent_course_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.get(f"/enrollments/courses/{non_existent_course_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"

def test_force_deregister_student_as_admin_success():
    student_id = create_student_user()
    course_id = create_course("API Design", "APD201")

    # Enroll as student
    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    post_response = client.post("/enrollments/", json={"user_id": student_id, "course_id": course_id})
    enrollment_id = post_response.json()["id"]
    app.dependency_overrides = {}

    # Admin force deregisters
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    response = client.delete(f"/enrollments/admin/{enrollment_id}")
    assert response.status_code == 204
    assert len(get_all_enrollments()) == 0

def test_force_deregister_non_existent_enrollment_as_admin_fails():
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    non_existent_enrollment_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.delete(f"/enrollments/admin/{non_existent_enrollment_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Enrollment not found"

def test_force_deregister_as_student_fails():
    student_id = create_student_user()
    course_id = create_course("Intro to Testing", "TST101")

    # Enroll as student first
    app.dependency_overrides[require_student_role] = lambda: UserRole.student
    post_response = client.post("/enrollments/", json={"user_id": student_id, "course_id": course_id})
    enrollment_id = post_response.json()["id"]
    app.dependency_overrides = {}

    # Student tries to use admin force-deregister endpoint
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.student
    response = client.delete(f"/enrollments/admin/{enrollment_id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Nahh!!, You must be an Admin to get this working."
