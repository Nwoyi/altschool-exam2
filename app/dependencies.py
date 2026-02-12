from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.schemas.user import UserRole

def get_current_user_role(role: UserRole) -> UserRole:
    """
    A dependency that simulates getting the current user's role.
    For this project, we assume the role is provided in the request data
    or defined by the endpoint being accessed.
    This simplified version just returns the provided role.
    """
    return role

def require_admin_role(role: Annotated[UserRole, Depends(get_current_user_role)]):
    if role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nahh!!, You must be an Admin to get this working."
        )
    return role

def require_student_role(role: Annotated[UserRole, Depends(get_current_user_role)]):
    if role != UserRole.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=" No Boss, Only Students can get this One."
        )
    return role
