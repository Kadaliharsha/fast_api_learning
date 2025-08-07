from fastapi import FastAPI
from app.db import engine
from app.models import user, project as project_model
from app.routers import auth
from app.routers import project as project_router
from app.routers import task as task_router

# Create database tables for all models
user.Base.metadata.create_all(bind=engine)
project_model.Base.metadata.create_all(bind=engine)

# Create the FastAPI application instance
app = FastAPI(title="Task Management API", version="1.0.0")

@app.get('/')
def read_root():
    return {"message": "Welcome to the Task Manager API!"}

# Include all the routers in the application
app.include_router(auth.router)  # Authentication endpoints
app.include_router(project_router.router)  # Project management endpoints
app.include_router(task_router.router)  # Task management endpoints
