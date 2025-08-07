from fastapi import FastAPI
from app.db import engine
from app.models import user, project as project_model
from app.routers import auth
from app.routers import project as project_router

user.Base.metadata.create_all(bind=engine)
project_model.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "Welcome to the Task Manager API!"}

app.include_router(auth.router)
app.include_router(project_router.router)
