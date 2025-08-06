from fastapi import FastAPI
from app.db import engine
from app.models import user
from app.routers import auth

user.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "Welcome to the Task Manager API!"}

app.include_router(auth.router)
