from fastapi.testclient import TestClient
from main import app
from app.crud.users import get_users
from app.in_memory_db import DB
import pytest
from uuid import UUID

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_around_tests():
    # Before each test, clear the DB
    DB["users"].clear()
    DB["courses"].clear()
    DB["enrollments"].clear()
    yield
    # After each test, clear the DB again
    DB["users"].clear()
    DB["courses"].clear()
    DB["enrollments"].clear()

def test_create_user():
    response = client.post(
        "/users/",
        json={"name": "Philip Onyema", "email": "philip@example.com", "role": "student"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Philip Onyema"
    assert data["email"] == "philip@example.com"
    assert data["role"] == "student"
    assert "id" in data
    assert len(get_users()) == 1

def test_create_user_invalid_email():
    response = client.post(
        "/users/",
        json={"name": "Tunde Bakare", "email": "tunde-not-valid", "role": "admin"}
    )
    assert response.status_code == 422

def test_create_user_empty_name():
    response = client.post(
        "/users/",
        json={"name": "", "email": "noname@example.com", "role": "student"}
    )
    assert response.status_code == 422

def test_create_user_invalid_role():
    response = client.post(
        "/users/",
        json={"name": "Kemi Adesanya", "email": "kemi@example.com", "role": "superadmin"}
    )
    assert response.status_code == 422

def test_create_user_email_already_registered():
    client.post(
        "/users/",
        json={"name": "Philip Onyema", "email": "philip@example.com", "role": "student"}
    )
    response = client.post(
        "/users/",
        json={"name": "Philip O", "email": "philip@example.com", "role": "admin"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_read_users():
    client.post("/users/", json={"name": "Philip Onyema", "email": "philip@example.com", "role": "student"})
    client.post("/users/", json={"name": "Mr Rotimi", "email": "rotimi@altschool.com", "role": "admin"})

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(u["email"] == "philip@example.com" for u in data)
    assert any(u["email"] == "rotimi@altschool.com" for u in data)

def test_read_single_user():
    post_response = client.post(
        "/users/",
        json={"name": "Chioma Nwosu", "email": "chioma@example.com", "role": "student"}
    )
    user_id = post_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == "Chioma Nwosu"

def test_read_single_user_not_found():
    non_existent_id = UUID("12345678-1234-5678-1234-567812345678")
    response = client.get(f"/users/{non_existent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_read_single_user_invalid_uuid():
    invalid_uuid = "not-a-uuid"
    response = client.get(f"/users/{invalid_uuid}")
    assert response.status_code == 422
