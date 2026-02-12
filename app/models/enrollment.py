from uuid import UUID

class Enrollment:
    def __init__(self, id: UUID, user_id: UUID, course_id: UUID):
        self.id = id
        self.user_id = user_id
        self.course_id = course_id

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "course_id": str(self.course_id)
        }
