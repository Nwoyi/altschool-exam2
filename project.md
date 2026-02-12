Project Exam: Course Enrollment Management API
Project Title: Design and Test a Course Enrollment Management API Using FastAPI

Project Overview
You are required to build a RESTful API using FastAPI that manages a course enrollment system.

The system must support:

Public access to course information
User-based roles (student and admin)
Role-based restrictions on certain operations
Student enrollment and deregistration from courses
This project focuses on handling relationships, validation, and role-based logic while using in-memory data storage.

⚠️ Important Note:
Authentication is not required.
You may assume the role of a user is provided in the request data.

Entities
Your system must include the following entities:

1. User
id
name
email
role (student or admin)

2. Course
id
title
code

3. Enrollment
id
user_id
course_id

Functional Requirements
1. User Management
Create a user
Retrieve all users
Retrieve a user by ID
Validation rules:

name must not be empty
email must be a valid email format
role must be either student or admin
2. Course Access
Public Access
The following actions must be accessible to any user:

Retrieve all courses
Retrieve a course by ID
Admin-Only Access
Only users with the role admin are allowed to:

Create a course
Update a course
Delete a course
Validation rules:

title must not be empty
code must not be empty and must be unique
3. Enrollment Management (Students)
Enroll a student in a course
Deregister a student from a course
Retrieve enrollments for a specific student
Rules:

Only users with role student can enroll or deregister
A student cannot enroll in the same course more than once
Enrollment must fail if the student or course does not exist
Deregistration must fail if the enrollment does not exist
4. Admin Enrollment Oversight
Admins must be able to:

Retrieve all enrollments
Retrieve enrollments for a specific course
Force deregister a student from a course
Technical Requirements
Use an in-memory data store (e.g. lists or dictionaries)
Apply data validation to all input data
Use appropriate HTTP status codes
Organize your code into multiple files and folders
Write API tests for all endpoints
Testing Requirements (Mandatory)
Your automated tests must:

Cover all endpoints
Test role-based behavior (student vs admin)
⚠️ Important:
You must run and pass all tests before submission.
Projects with failing tests will be penalized.

What Is NOT Required
Authentication or authorization mechanisms
Database or ORM usage
Frontend application
External services
Submission Requirements
Submit:

The complete FastAPI project
All test files
A README.md explaining:
How to run the API
How to run the tests
Assessment Criteria
You will be graded based on:

Correct role-based behavior
Proper handling of entity relationships
Data validation quality
Test coverage and reliability
Code clarity and organization
Final Instruction to Students
Do not submit your project without running and passing your tests.
A working, well-tested API is the goal of this assignment.