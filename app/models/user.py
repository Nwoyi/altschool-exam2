from uuid import UUID
from app.schemas.user import UserRole

class User:
    def __init__(self, id: UUID, name: str, email: str, role: UserRole):
        self.id = id
        self.name = name
        self.email = email
        self.role = role

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role.value
        }
