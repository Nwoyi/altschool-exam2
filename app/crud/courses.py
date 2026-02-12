from typing import List, Optional
from uuid import UUID, uuid4

from app.in_memory_db import DB
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate

def get_course(course_id: UUID) -> Optional[Course]:
    return DB["courses"].get(course_id)

def get_courses() -> List[Course]:
    return list(DB["courses"].values())

def get_course_by_code(code: str) -> Optional[Course]:
    for course in DB["courses"].values():
        if course.code == code:
            return course
    return None

def create_course(course_create: CourseCreate) -> Course:
    if get_course_by_code(course_create.code):
        return None # Code must be unique
    
    course_id = uuid4()
    course = Course(
        id=course_id,
        title=course_create.title,
        code=course_create.code
    )
    DB["courses"][course_id] = course
    return course

def update_course(course_id: UUID, course_update: CourseUpdate) -> Optional[Course]:
    existing_course = DB["courses"].get(course_id)
    if not existing_course:
        return None
    
    update_data = course_update.model_dump(exclude_unset=True)
    
    # Check if code is being updated and if it's unique
    if "code" in update_data and update_data["code"] != existing_course.code:
        if get_course_by_code(update_data["code"]):
            return None # New code must be unique
            
    for key, value in update_data.items():
        setattr(existing_course, key, value)
    
    DB["courses"][course_id] = existing_course # Update in DB (though object is already updated)
    return existing_course

def delete_course(course_id: UUID) -> Optional[Course]:
    return DB["courses"].pop(course_id, None)
