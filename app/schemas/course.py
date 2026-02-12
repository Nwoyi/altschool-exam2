from typing import Optional
from uuid import UUID # Import UUID
from pydantic import BaseModel, Field, ConfigDict # Import ConfigDict

class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the course.")
    code: str = Field(..., min_length=1, description="Unique course code.")

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Updated title of the course.")
    code: Optional[str] = Field(None, min_length=1, description="Updated unique course code.")

class CourseInDB(CourseBase):
    id: UUID = Field(..., description="Unique identifier for the course.")

    model_config = ConfigDict(from_attributes=True) # Use ConfigDict
