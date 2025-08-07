from pydantic import BaseModel

class ProjectCreate(BaseModel):
    title: str
    description: str = ""
    
class ProjectOut(ProjectCreate):
    id: int
    
    class Config:
        orm_mode = True