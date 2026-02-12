# FastAPI Project Best Practices

## 1. Project Structure
A well-organized project structure is crucial for maintainability and scalability. For this project, given its scope, a modular approach is suitable.

```
.

├── main.py                     # Main FastAPI application instance
├── app/
│   ├── __init__.py
│   ├── routers/                # Endpoint definitions
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── courses.py
│   │   └── enrollments.py
│   ├── models/                 # Pydantic models for data (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── course.py
│   │   └── enrollment.py
│   ├── crud/                   # Create, Read, Update, Delete operations (interacts with in-memory_db)
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── courses.py
│   │   └── enrollments.py
│   ├── in_memory_db.py         # In-memory data storage simulation
│   └── dependencies.py         # Dependency injection for common logic (e.g., role checking)
└── tests/                      # API tests
    ├── __init__.py
    ├── test_users.py
    ├── test_courses.py
    └── test_enrollments.py
```

**Explanation of directories:**
*   `main.py`: Entry point for the FastAPI application.
*   `app/routers/`: Contains route definitions for different entities (users, courses, enrollments). Each file will have `APIRouter` instances.
*   `app/models/`: Contains Pydantic models for defining the structure of request bodies (e.g., for creating a user) and response bodies. These will also serve as the schema for our in-memory data.
*   `app/crud/`: Houses functions that perform Create, Read, Update, and Delete operations on our in-memory data. This layer abstracts direct data manipulation from the routers.
*   `app/in_memory_db.py`: Centralized location for our in-memory data structures (dictionaries/lists) that simulate a database.
*   `app/dependencies.py`: For reusable logic that can be injected into route functions, such as role-based access control.
*   `tests/`: Contains test files for each component, ensuring all endpoints and logic work as expected.

## 2. Data Validation with Pydantic

FastAPI leverages Pydantic for data validation and serialization.

*   **Request Validation:** Pydantic models will be used to define the expected structure and types of incoming request bodies. FastAPI automatically validates the request data against these models.
*   **Response Validation/Serialization:** Pydantic models can also be used to define the structure of outgoing responses, ensuring consistent data types and automatically serializing Python objects to JSON.
*   **Custom Validation:** Pydantic allows for custom validators (e.g., `@validator` decorator) for more complex validation rules (e.g., email format, unique codes).

## 3. In-Memory Data Storage

As per project requirements, we will use in-memory data storage.

*   **Global Dictionaries/Lists:** The simplest approach is to use Python dictionaries or lists in a dedicated module (e.g., `app/in_memory_db.py`) to store our entities.
*   **Unique IDs:** Each entity (User, Course, Enrollment) will need a unique ID. We can use Python's `uuid` module to generate these.
*   **Simulating Relationships:** Relationships between entities (e.g., `user_id` and `course_id` in `Enrollment`) will be represented by storing the respective IDs.

**Example Structure for `in_memory_db.py`:**

```python
from typing import Dict, List
from uuid import UUID

# This would typically be populated from a database in a real application
DB: Dict[str, Dict] = {
    "users": {},
    "courses": {},
    "enrollments": {}
}
```

## 4. Testing with `pytest` and `httpx`

FastAPI is well-integrated with `pytest` for testing. `httpx` is recommended for making asynchronous HTTP requests in tests.

*   **`TestClient`:** FastAPI provides a `TestClient` from `starlette.testclient` (which uses `httpx`) that allows for synchronous requests against the asynchronous FastAPI application, making testing easier.
*   **Arrange-Act-Assert:** Follow the AAA pattern for tests:
    *   **Arrange:** Set up test data, mock dependencies.
    *   **Act:** Make the API call using `TestClient`.
    *   **Assert:** Verify the response status code, content, and any changes to the in-memory data.
*   **Role-Based Testing:** Crucially, tests must cover both `student` and `admin` roles to ensure correct access control for all endpoints. This means simulating requests from users with different roles.
*   **Validation Testing:** Test cases should explicitly check for invalid input and expect appropriate HTTP 4xx status codes.
*   **Edge Cases:** Test scenarios like non-existent IDs, attempting to enroll in the same course twice, etc.

**Example `TestClient` usage:**

```python
from fastapi.testclient import TestClient
from main import app # Assuming your FastAPI app instance is named 'app' in main.py

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
```