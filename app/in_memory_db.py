from typing import Dict, Any
from uuid import UUID

from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment


DB: Dict[str, Dict[UUID, Any]] = { # 'Any' is used here because the dict can store different model types (User, Course, Enrollment)
    "users": {}, # type: Dict[UUID, User]
    "courses": {}, # type: Dict[UUID, Course]
    "enrollments": {} # type: Dict[UUID, Enrollment]
}
