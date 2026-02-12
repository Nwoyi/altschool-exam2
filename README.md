# ALTSCHOol Course Enrollment Management API

This is a RESTful API built with FastAPI for managing a course enrollment system. It supports public access to course information, user roles (student and admin), and role-based restrictions on certain operations, including student enrollment/deregistration and admin oversight.

**Important Note:** This project uses in-memory data storage and does not implement full authentication As instructed in assisgnment By Sir Rotimi. User roles are assumed to be provided in the request data or context for simplicity.

## Features

*   **User Management:** Create, retrieve (all or by ID) users. Basic validation for name, email, and role.
*   **Course Access:**
    *   Public: Retrieve all courses, retrieve a course by ID.
    *   Admin-Only: Create, update, delete courses.
*   **Enrollment Management:**
    *   Student: Enroll in a course, deregister from a course, retrieve personal enrollments.
    *   Admin: Retrieve all enrollments, retrieve enrollments for a specific course, force deregister students.

## Project Structure

The project is organized into several modules to keep the code clean and maintainable:

```
.
├── main.py                     # Main FastAPI application instance
├── app/
│   ├── routers/                # Defines API endpoints (users, courses, enrollments)
│   ├── models/                 # Python classes for in-memory data objects (User, Course, Enrollment)
│   ├── crud/                   # Functions for interacting with in-memory data (Create, Read, Update, Delete)
│   ├── schemas/                # Pydantic models for request/response data validation and serialization
│   ├── in_memory_db.py         # Simple in-memory storage (Python dictionaries)
│   └── dependencies.py         # Helper functions for role-based access control
└── tests/                      # Automated API tests
```

## Setup and Run

### Prerequisites

*   Python 3.9+
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd altschool-exam2
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install fastapi uvicorn pydantic email-validator python-multipart
    pip install pytest httpx
    ```
    *(Note: `pydantic[email]` installs `email-validator` for email validation.)*

### Running the API

To start the API server, navigate to the project's root directory and run:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

### Running Tests

To run the automated tests, ensure your virtual environment is active and run `pytest` from the project's root directory, Simple:

```bash
pytest tests/
```

All tests should pass, covering endpoint functionality, data validation, and role-based behavior.

## API Endpoints (Overview)

All endpoints listed below are relative to the base URL (`http://127.0.0.1:8000`).

### User Management (`/users`)

*   `POST /users/`: To Create a new user. (Accessible by anyone, for this project)
*   `GET /users/`: To Retrieve a list of all users. (Accessible by anyone, for this project)
*   `GET /users/{user_id}`:To Retrieve a single user by ID. (Accessible by anyone, for this project)

### Course Access (`/courses`)

*   `GET /courses/`: To Retrieve a list of all courses. (Public Access)
*   `GET /courses/{course_id}`:To Retrieve a single course by ID. (Public Access)
*   `POST /courses/`: To Create a new course. (Admin-Only)
*   `PUT /courses/{course_id}`:To Update an existing course. (Admin-Only)
*   `DELETE /courses/{course_id}`: To Delete a course. (Admin-Only)

### Enrollment Management (`/enrollments`)

*   `POST /enrollments/`: For Enroll a student in a course. (Student-Only)
*   `DELETE /enrollments/{enrollment_id}`: To Deregister a student from their enrollment. (Student-Only)
*   `GET /enrollments/users/{user_id}`: For Retrieving enrollments for a specific student. (Student-Only)
*   `GET /enrollments/`:For  Retrieving all enrollments. (Admin-Only)
*   `GET /enrollments/courses/{course_id}`:This si to Retrieve all enrollments for a specific course. (Admin-Only)
*   `DELETE /enrollments/admin/{enrollment_id}`: Force deregister a student from an enrollment. (Admin-Only)

## Contributing

Pull requests are welcome 🙂. For major changes, please open an issue first to discuss what you would like to change. So i get more marks lol
