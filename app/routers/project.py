from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.auth.oauth2 import get_current_user
from app.models.user import User
from typing import Optional


router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectOut)
def create_project(
    project: ProjectCreate,  # Pydantic model for request validation
    db: Session = Depends(get_db),  # Database session dependency
    current_user: User = Depends(get_current_user)  # Current authenticated user
):
    """
    Create a new project for the authenticated user.
    
    Args:
        project: Project data from request body
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        ProjectOut: Created project with generated ID
    """
    # Create a new Project instance with the provided data
    new_project = Project(
        title=project.title, 
        description=project.description, 
        owner_id=current_user.id  # Set the current user as the project owner
    )
    # Add the project to the database session (stages the insert)
    db.add(new_project)
    # Commit the transaction to actually save the project to database
    db.commit()
    # Refresh the object to get the generated ID and any database defaults
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=list[ProjectOut])
def get_projects(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Get all projects owned by the authenticated user.
    
    Args:
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        List[ProjectOut]: List of all projects owned by the user
    """
    # Query all projects where the owner_id matches the current user's ID
    # This ensures users can only see their own projects (security)
    return db.query(Project).filter(Project.owner_id == current_user.id).all()

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,  # Path parameter - the ID of the project to retrieve
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific project by ID.
    
    Args:
        project_id: ID of the project to retrieve (from URL path)
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        ProjectOut: The requested project
    
    Raises:
        HTTPException: 404 if project not found, 403 if user not authorized
    """
    # Query the project by its ID
    project = db.query(Project).filter(Project.id == project_id).first()
    
    # Check if the project exists
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Authorization check: ensure the current user owns this project
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
    
    return project

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,  # Path parameter - the ID of the project to update
    project_update: ProjectUpdate,  # Pydantic model for partial updates
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a project (partial update - only provided fields are updated).
    
    Args:
        project_id: ID of the project to update (from URL path)
        project_update: Partial update data from request body
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        ProjectOut: Updated project
    
    Raises:
        HTTPException: 404 if project not found, 403 if user not authorized
    """
    # Query the project by its ID
    project = db.query(Project).filter(Project.id == project_id).first()
    
    # Check if the project exists
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Authorization check: ensure the current user owns this project
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")
    
    # Get only the fields that were actually provided in the request
    # exclude_unset=True means we ignore fields that weren't sent
    update_data = project_update.dict(exclude_unset=True)
    
    # Update each provided field on the project object
    for field, value in update_data.items():
        setattr(project, field, value)  # Dynamically set the field value
    
    # Commit the changes to the database
    db.commit()
    # Refresh the object to get any updated values (like updated timestamps)
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,  # Path parameter - the ID of the project to delete
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project and all its associated tasks.
    
    Args:
        project_id: ID of the project to delete (from URL path)
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        dict: Success message
    
    Raises:
        HTTPException: 404 if project not found, 403 if user not authorized
    """
    # Query the project by its ID
    project = db.query(Project).filter(Project.id == project_id).first()
    
    # Check if the project exists
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Authorization check: ensure the current user owns this project
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    # Delete the project from the database
    # Note: Due to cascade="all, delete-orphan" in the Project model,
    # all associated tasks will also be automatically deleted
    db.delete(project)
    db.commit()
    
    # Return a success message instead of the deleted object
    # (since the object is no longer in the database)
    return {"detail": "Project deleted successfully"}



