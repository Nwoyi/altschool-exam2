from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.course import CourseCreate, CourseUpdate, CourseInDB
from app.crud import courses as crud_courses
from app.dependencies import require_admin_role

router = APIRouter(prefix="/courses", tags=["Courses"])

# Public Access - no role needed, anyone can view courses
@router.get("/", response_model=List[CourseInDB])
async def read_courses():
    courses = crud_courses.get_courses()
    return [CourseInDB.model_validate(course) for course in courses]

@router.get("/{course_id}", response_model=CourseInDB)
async def read_course(course_id: UUID):
    course = crud_courses.get_course(course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course could not b found")
    return CourseInDB.model_validate(course)

# Admin-Only Access
@router.post("/", response_model=CourseInDB, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    admin_role: str = Depends(require_admin_role)
):
    db_course = crud_courses.get_course_by_code(course.code)
    if db_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This Course with this code already exists"
        )
    
    created_course = crud_courses.create_course(course)
    if not created_course:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Api Failed to create course"
        )
    return CourseInDB.model_validate(created_course)

@router.put("/{course_id}", response_model=CourseInDB)
async def update_course(
    course_id: UUID,
    course: CourseUpdate,
    admin_role: str = Depends(require_admin_role)
):
    updated_course = crud_courses.update_course(course_id, course)
    if updated_course is None:
        if crud_courses.get_course(course_id) is None: # Check if course exists at all
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course could not be found")
        else: # Code conflict
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course with this code already exists")
    return CourseInDB.model_validate(updated_course)

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    admin_role: str = Depends(require_admin_role)
):
    deleted_course = crud_courses.delete_course(course_id)
    if deleted_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return # 204 No Content
