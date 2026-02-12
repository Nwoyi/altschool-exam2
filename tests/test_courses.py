from fastapi.testclient import TestClient
from main import app
from app.crud.courses import get_courses
from app.in_memory_db import DB
from app.schemas.user import UserRole
from app.dependencies import require_admin_role, get_current_user_role
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

# Helper to create an admin user
def create_admin_user():
    response = client.post(
        "/users/",
        json={"name": "Mr Rotimi", "email": "rotimi@altschool.com", "role": "admin"}
    )
    assert response.status_code == 201
    return response.json()["id"]

# Helper to create a student user
def create_student_user():
    response = client.post(
        "/users/",
        json={"name": "Philip Onyema", "email": "philip@example.com", "role": "student"}
    )
    assert response.status_code == 201
    return response.json()["id"]

# --- Test Course Creation (Admin Only) ---
def test_create_course_as_admin():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin

    response = client.post(
        "/courses/",
        json={"title": "Backend Python", "code": "BEP101"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Backend Python"
    assert data["code"] == "BEP101"
    assert "id" in data
    assert len(get_courses()) == 1

def test_create_course_as_student_fails():
    create_student_user()
    # Override to simulate student trying to access admin endpoint
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.student

    response = client.post(
        "/courses/",
        json={"title": "Frontend React", "code": "FER201"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Nahh!!, You must be an Admin to get this working."

def test_create_course_duplicate_code_as_admin():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin

    client.post("/courses/", json={"title": "Backend Node JS", "code": "BEN101"})
    response = client.post(
        "/courses/",
        json={"title": "Backend Express", "code": "BEN101"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "This Course with this code already exists"

def test_create_course_invalid_title():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin

    response = client.post(
        "/courses/",
        json={"title": "", "code": "INV001"}
    )
    assert response.status_code == 422

# --- Test Course Retrieval (Public) ---
def test_read_courses():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    client.post("/courses/", json={"title": "Backend Python", "code": "BEP101"})
    client.post("/courses/", json={"title": "Frontend HTML CSS", "code": "FEH101"})
    app.dependency_overrides = {}

    response = client.get("/courses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(c["code"] == "BEP101" for c in data)
    assert any(c["code"] == "FEH101" for c in data)

def test_read_single_course():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    post_response = client.post(
        "/courses/",
        json={"title": "Data Structures and Algorithms", "code": "DSA301"}
    )
    course_id = post_response.json()["id"]
    app.dependency_overrides = {}

    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == course_id
    assert data["title"] == "Data Structures and Algorithms"

def test_read_single_course_not_found():
    non_existent_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.get(f"/courses/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course could not b found"

# --- Test Course Update (Admin Only) ---
def test_update_course_as_admin():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    post_response = client.post(
        "/courses/",
        json={"title": "Intro to Cloud Computing", "code": "CLD100"}
    )
    course_id = post_response.json()["id"]

    update_response = client.put(
        f"/courses/{course_id}",
        json={"title": "Advanced Cloud Computing", "code": "CLD200"}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["id"] == course_id
    assert data["title"] == "Advanced Cloud Computing"
    assert data["code"] == "CLD200"

def test_update_course_as_student_fails():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    post_response = client.post(
        "/courses/",
        json={"title": "DevOps Basics", "code": "DOP101"}
    )
    course_id = post_response.json()["id"]
    app.dependency_overrides = {}

    # Now simulate student trying to update
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.student

    response = client.put(
        f"/courses/{course_id}",
        json={"title": "DevOps Advanced"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Nahh!!, You must be an Admin to get this working."

def test_update_course_not_found():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    non_existent_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.put(
        f"/courses/{non_existent_id}",
        json={"title": "This Course Doesnt Exist"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Course could not be found"

def test_update_course_duplicate_code():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin

    client.post("/courses/", json={"title": "Backend Python", "code": "BEP101"})
    post_response = client.post("/courses/", json={"title": "Backend Node JS", "code": "BEN101"})
    node_course_id = post_response.json()["id"]

    response = client.put(
        f"/courses/{node_course_id}",
        json={"code": "BEP101"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Course with this code already exists"

# --- Test Course Deletion (Admin Only) ---
def test_delete_course_as_admin():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    post_response = client.post(
        "/courses/",
        json={"title": "Intro to Testing", "code": "TST101"}
    )
    course_id = post_response.json()["id"]

    response = client.delete(f"/courses/{course_id}")
    assert response.status_code == 204
    assert len(get_courses()) == 0

def test_delete_course_as_student_fails():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    post_response = client.post(
        "/courses/",
        json={"title": "API Design", "code": "APD201"}
    )
    course_id = post_response.json()["id"]
    app.dependency_overrides = {}

    # Simulate student trying to delete
    app.dependency_overrides[get_current_user_role] = lambda: UserRole.student

    response = client.delete(f"/courses/{course_id}")
    assert response.status_code == 403
    assert response.json()["detail"] == "Nahh!!, You must be an Admin to get this working."

def test_delete_course_not_found():
    create_admin_user()
    app.dependency_overrides[require_admin_role] = lambda: UserRole.admin
    non_existent_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.delete(f"/courses/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Course not found"
