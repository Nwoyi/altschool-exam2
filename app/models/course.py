from uuid import UUID

class Course:
    def __init__(self, id: UUID, title: str, code: str):
        self.id = id
        self.title = title
        self.code = code

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "code": self.code
        }
