from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, ConfigDict # Import ConfigDict

class UserRole(str, Enum):
    student = "student"
    admin = "admin"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, description="User's full name.")
    email: EmailStr = Field(..., description="User's email address.")
    role: UserRole = Field(..., description="User's role (student or admin).")

class UserCreate(UserBase):
    pass

class UserInDB(UserBase):
    id: UUID = Field(..., description="Unique identifier for the user.")

    model_config = ConfigDict(from_attributes=True) # Use ConfigDict
