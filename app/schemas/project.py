from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    """
    Schema for creating a new project.
    Used for POST /projects/ endpoint.
    """
    title: str  # Required project title
    description: str = ""  # Optional description with default empty string
    
class ProjectOut(ProjectCreate):
    """
    Schema for project responses.
    Extends ProjectCreate and adds the database-generated ID.
    Used for all GET endpoints that return project data.
    """
    id: int  # Database-generated primary key
    
    class Config:
        from_attributes = True  # Allows Pydantic to work with SQLAlchemy models
        
class ProjectUpdate(BaseModel):
    """
    Schema for updating a project (partial updates).
    All fields are optional - only provided fields will be updated.
    Used for PATCH /projects/{id} endpoint.
    """
    title: Optional[str] = None  # Optional new title
    description: Optional[str] = None  # Optional new description
    
    class Config:
        from_attributes = True  # Allows Pydantic to work with SQLAlchemy models