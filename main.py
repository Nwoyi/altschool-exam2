from fastapi import FastAPI
from app.routers import users, courses, enrollments

app = FastAPI(
    title="Course Enrollment Management API",
    description="API for managing course enrollments with user roles and in-memory data storage.",
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Course Enrollment Management API"}
