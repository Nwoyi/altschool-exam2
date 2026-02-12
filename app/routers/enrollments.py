from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.enrollment import EnrollmentCreate, EnrollmentInDB
from app.schemas.user import UserRole
from app.crud import enrollments as crud_enrollments
from app.crud import users as crud_users
from app.crud import courses as crud_courses
from app.dependencies import require_admin_role, require_student_role, get_current_user_role

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)

# Student Access
@router.post("/", response_model=EnrollmentInDB, status_code=status.HTTP_201_CREATED)
async def enroll_student_in_course(
    enrollment_data: EnrollmentCreate,
    student_role: UserRole = Depends(require_student_role) # Only students can enroll
):
    user_id = enrollment_data.user_id # Removed redundant UUID()
    course_id = enrollment_data.course_id # Removed redundant UUID()

    # Validate user and course existence
    user = crud_users.get_user(user_id)
    if not user or user.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or not a student")
    
    course = crud_courses.get_course(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    # Check if already enrolled
    existing_enrollment = crud_enrollments.get_enrollment_by_user_and_course(user_id, course_id)
    if existing_enrollment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student already enrolled in this course")

    enrollment = crud_enrollments.create_enrollment(user_id, course_id)
    return EnrollmentInDB.model_validate(enrollment)

@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deregister_student_from_course(
    enrollment_id: UUID,
    student_role: UserRole = Depends(require_student_role) # Only students can deregister their own
):
    enrollment = crud_enrollments.get_enrollment(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    
    # Ensure the student is deregistering their own enrollment (simplified for this project)
    # In a real app, this would compare current_user_id with enrollment.user_id
    # For now, we assume if a student calls this, it's for their own.
    # The actual user ID check is omitted for project simplicity (no auth)
    
    deleted_enrollment = crud_enrollments.delete_enrollment(enrollment_id)
    if deleted_enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return

@router.get("/users/{user_id}", response_model=List[EnrollmentInDB])
async def get_enrollments_for_student(
    user_id: UUID,
    student_role: UserRole = Depends(require_student_role) # Only students can view their own enrollments
):
    user = crud_users.get_user(user_id)
    if not user or user.role != UserRole.student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found or not a student")

    # Ensure the student is viewing their own enrollments
    # For this project, assume the 'user_id' in the path corresponds to the 'student_role' user.
    # In a real application, current_user_id would be compared to user_id.

    enrollments = crud_enrollments.get_enrollments_for_user(user_id)
    return [EnrollmentInDB.model_validate(enrollment) for enrollment in enrollments]

# Admin Oversight
@router.get("/", response_model=List[EnrollmentInDB])
async def get_all_enrollments(
    admin_role: UserRole = Depends(require_admin_role) # Only admins can view all enrollments
):
    enrollments = crud_enrollments.get_all_enrollments()
    return [EnrollmentInDB.model_validate(enrollment) for enrollment in enrollments]

@router.get("/courses/{course_id}", response_model=List[EnrollmentInDB])
async def get_enrollments_by_course(
    course_id: UUID,
    admin_role: UserRole = Depends(require_admin_role) # Only admins can view enrollments for a course
):
    course = crud_courses.get_course(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    enrollments = crud_enrollments.get_enrollments_for_course(course_id)
    return [EnrollmentInDB.model_validate(enrollment) for enrollment in enrollments]

@router.delete("/admin/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def force_deregister_student(
    enrollment_id: UUID,
    admin_role: UserRole = Depends(require_admin_role) # Only admins can force deregister
):
    deleted_enrollment = crud_enrollments.delete_enrollment(enrollment_id)
    if deleted_enrollment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return
