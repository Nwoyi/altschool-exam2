from typing import List, Optional
from uuid import UUID, uuid4

from app.in_memory_db import DB
from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, UserRole

def get_user(user_id: UUID) -> Optional[User]:
    return DB["users"].get(user_id)

def get_users() -> List[User]:
    return list(DB["users"].values())

def get_user_by_email(email: str) -> Optional[User]:
    for user in DB["users"].values():
        if user.email == email:
            return user
    return None

def create_user(user_create: UserCreate) -> User:
    if get_user_by_email(user_create.email):
        # In a real app, this would raise an HTTPException, but CRUD functions typically don't
        # raise HTTP exceptions directly. The router will handle this.
        return None 
    
    user_id = uuid4()
    user = User(
        id=user_id,
        name=user_create.name,
        email=user_create.email,
        role=user_create.role
    )
    DB["users"][user_id] = user
    return user
