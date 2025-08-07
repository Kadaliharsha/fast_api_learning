from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut
from app.auth.oauth2 import get_current_user
from app.models.user import User

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectOut)
def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    new_project = Project(
        title=project.title, 
        description=project.description, 
        owner_id=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=list[ProjectOut])
def get_projects(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return db.query(Project).filter(Project.owner_id == current_user.id).all()


