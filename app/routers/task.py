from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.project import Task, Project
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead
from app.auth.oauth2 import get_current_user
from app.models.user import User
# Import email tasks only when needed to avoid Redis connection issues
# from app.tasks.email_tasks import send_task_assignment_email, send_task_status_change_email
from typing import List, Optional
from sqlalchemy import or_
from datetime import datetime


router = APIRouter(prefix="/tasks", tags=["tasks"])

def send_email_notification_safely(task_type: str, **kwargs):
    """
    Safely send email notifications without failing the main operation.
    
    Args:
        task_type: Type of email notification ('assignment' or 'status_change')
        **kwargs: Arguments for the email task
    """
    # Email notifications are temporarily disabled due to Redis connection issues
    # TODO: Enable email notifications when Redis connection is stable
    print(f"Email notification ({task_type}) would be sent here in production")
    return True

@router.post('/', response_model=TaskRead)
def create_task(
    task: TaskCreate,  # Pydantic model for request validation
    db: Session = Depends(get_db),  # Database session dependency
    current_user: User = Depends(get_current_user)  # Current authenticated user
):
    """
    Create a new task.
    
    Args:
        task: Task data from request body
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        TaskRead: Created task with generated ID
    """
    # Create a new Task instance with the provided data
    new_task = Task(
        title=task.title, 
        description=task.description, 
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
        assigned_user_id=task.assigned_user_id
    )
    # Add the task to the database session (stages the insert)
    db.add(new_task)
    # Commit the transaction to actually save the task to database
    db.commit()
    # Refresh the object to get the generated ID and any database defaults
    db.refresh(new_task)
    
    # Send background email notification if task is assigned to someone else
    if new_task.assigned_user_id is not None and new_task.assigned_user_id != current_user.id:  # type: ignore
        # Queue the email task to run in the background
        # This allows the API to respond quickly while email is sent asynchronously
        send_email_notification_safely(
            task_type='assignment',
            task_id=new_task.id,
            assigned_user_id=new_task.assigned_user_id,
            assigned_by_id=current_user.id
        )
    
    return new_task

@router.get("/", response_model=List[TaskRead])
def list_tasks(
    status: Optional[str] = None,  # Filter by task status
    priority: Optional[str] = None,  # Filter by task priority
    due_date: Optional[str] = None,  # Filter by due date (YYYY-MM-DD format)
    project_id: Optional[int] = None,  # Filter by project ID
    sort_by: Optional[str] = None,  # Sort by field (priority, due_date)
    limit: int = 10,  # Number of tasks to return (pagination)
    offset: int = 0,  # Number of tasks to skip (pagination)
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of tasks with filtering, sorting, and pagination.
    
    Users can see tasks from projects they own OR tasks assigned to them.
    
    Args:
        status: Filter by task status (todo, in_progress, done)
        priority: Filter by priority (low, medium, high)
        due_date: Filter by due date (YYYY-MM-DD format)
        project_id: Filter by project ID
        sort_by: Sort by field (priority, due_date)
        limit: Number of tasks to return
        offset: Number of tasks to skip
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        List[TaskRead]: List of tasks matching the criteria
    """
    # Build the base query joining Task with Project
    # This allows us to filter by project ownership
    query = db.query(Task).join(Project).filter(
        # Users can see tasks from projects they own OR tasks assigned to them
        or_(
            Project.owner_id == current_user.id,
            Task.assigned_user_id == current_user.id
        )
    )
    
    # Apply filters if provided
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if due_date:
        try:
            # Convert string date to datetime object for comparison
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            query = query.filter(Task.due_date == due_date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format. Use YYYY-MM-DD.")
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    # Apply sorting if provided
    if sort_by in ["priority", "due_date"]:
        query = query.order_by(getattr(Task, sort_by))
    elif sort_by:
        raise HTTPException(status_code=400, detail="Invalid sort_by field.")
    
    # Apply pagination
    tasks = query.offset(offset).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,  # Path parameter - the ID of the task to retrieve
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by ID.
    
    Args:
        task_id: ID of the task to retrieve (from URL path)
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        TaskRead: The requested task
    
    Raises:
        HTTPException: 404 if task not found, 403 if user not authorized
    """
    # Query the task by its ID
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Authorization check: user can view if they own the project OR are assigned to the task
    if not (
        task.project.owner_id == current_user.id or
        task.assigned_user_id == current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return task

@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,  # Path parameter - the ID of the task to update
    task_update: TaskUpdate,  # Pydantic model for partial updates
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a task (partial update - only provided fields are updated).
    
    Args:
        task_id: ID of the task to update (from URL path)
        task_update: Partial update data from request body
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        TaskRead: Updated task
    
    Raises:
        HTTPException: 404 if task not found, 403 if user not authorized
    """
    # Query the task by its ID
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Authorization check: user can update if they own the project OR are assigned to the task
    if not (
        task.project.owner_id == current_user.id or 
        task.assigned_user_id == current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    # Store old values for email notifications
    old_status = task.status
    old_assigned_user_id = task.assigned_user_id
    
    # Get only the fields that were actually provided in the request
    # exclude_unset=True means we ignore fields that weren't sent
    update_data = task_update.dict(exclude_unset=True)
    
    # Update each provided field on the task object
    for field, value in update_data.items():
        setattr(task, field, value)  # Dynamically set the field value
    
    # Commit the changes to the database
    db.commit()
    # Refresh the object to get any updated values (like updated timestamps)
    db.refresh(task)
    
    # Queue background email notifications for changes
    
    # 1. Status change notification
    if 'status' in update_data and old_status != task.status:
        # Only notify if there's an assigned user and it's not the person making the change
        if task.assigned_user_id is not None and task.assigned_user_id != current_user.id:
            # Queue the background task for status change notification
            send_email_notification_safely(
                task_type='status_change',
                task_id=task.id,
                user_id=task.assigned_user_id,
                changed_by_id=current_user.id,
                old_status=old_status,
                new_status=task.status
            )
    
    # 2. Assignment change notification
    if 'assigned_user_id' in update_data and old_assigned_user_id != task.assigned_user_id:
        # Only notify if there's a newly assigned user
        if task.assigned_user_id is not None:
            # Queue the background task for assignment notification
            send_email_notification_safely(
                task_type='assignment',
                task_id=task.id,
                assigned_user_id=task.assigned_user_id,
                assigned_by_id=current_user.id
            )
    
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,  # Path parameter - the ID of the task to delete
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.
    
    Args:
        task_id: ID of the task to delete (from URL path)
        db: Database session
        current_user: Authenticated user from JWT token
    
    Returns:
        dict: Success message
    
    Raises:
        HTTPException: 404 if task not found, 403 if user not authorized
    """
    # Query the task by its ID
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only project owner can delete tasks (more restrictive than update)
    if task.project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    # Delete the task from the database
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}