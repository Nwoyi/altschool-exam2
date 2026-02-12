from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreate, UserInDB
from app.crud import users as crud_users

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # Check if email is already taken
    db_user = crud_users.get_user_by_email(user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    created_user = crud_users.create_user(user)
    if not created_user:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    return UserInDB.model_validate(created_user)

@router.get("/", response_model=List[UserInDB])
async def read_users():
    users = crud_users.get_users()
    return [UserInDB.model_validate(user) for user in users]

@router.get("/{user_id}", response_model=UserInDB)
async def read_user(user_id: UUID):
    user = crud_users.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserInDB.model_validate(user)
