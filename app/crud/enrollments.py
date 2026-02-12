from typing import List, Optional
from uuid import UUID, uuid4

from app.in_memory_db import DB
from app.models.enrollment import Enrollment

def get_enrollment(enrollment_id: UUID) -> Optional[Enrollment]:
    return DB["enrollments"].get(enrollment_id)

def get_enrollments_for_user(user_id: UUID) -> List[Enrollment]:
    return [
        enrollment for enrollment in DB["enrollments"].values()
        if enrollment.user_id == user_id
    ]

def get_enrollments_for_course(course_id: UUID) -> List[Enrollment]:
    return [
        enrollment for enrollment in DB["enrollments"].values()
        if enrollment.course_id == course_id
    ]

def get_all_enrollments() -> List[Enrollment]:
    return list(DB["enrollments"].values())

def get_enrollment_by_user_and_course(user_id: UUID, course_id: UUID) -> Optional[Enrollment]:
    for enrollment in DB["enrollments"].values():
        if enrollment.user_id == user_id and enrollment.course_id == course_id:
            return enrollment
    return None

def create_enrollment(user_id: UUID, course_id: UUID) -> Enrollment:
    enrollment_id = uuid4()
    enrollment = Enrollment(
        id=enrollment_id,
        user_id=user_id,
        course_id=course_id
    )
    DB["enrollments"][enrollment_id] = enrollment
    return enrollment

def delete_enrollment(enrollment_id: UUID) -> Optional[Enrollment]:
    return DB["enrollments"].pop(enrollment_id, None)
