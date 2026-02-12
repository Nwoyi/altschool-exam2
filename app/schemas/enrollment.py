from pydantic import BaseModel, Field, ConfigDict # Import ConfigDict
from uuid import UUID

class EnrollmentBase(BaseModel):
    user_id: UUID = Field(..., description="ID of the student user.") # Changed to UUID
    course_id: UUID = Field(..., description="ID of the course.") # Changed to UUID

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentInDB(EnrollmentBase):
    id: UUID = Field(..., description="Unique identifier for the enrollment.") # Changed to UUID

    model_config = ConfigDict(from_attributes=True) # Use ConfigDict
