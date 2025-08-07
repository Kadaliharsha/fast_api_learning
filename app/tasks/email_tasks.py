from celery import shared_task
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.project import Task, Project
from app.models.user import User
from app.utils.email_service import email_service
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db() -> Session:
    """
    Get a database session for background tasks.
    This is a simple version - in production you might want connection pooling.
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Failed to get database session: {e}")
        raise

@shared_task(bind=True, max_retries=3)
def send_task_assignment_email(self, task_id: int, assigned_user_id: int, assigned_by_id: int) -> bool:
    """
    Background task to send task assignment notification email.
    
    Args:
        task_id: ID of the assigned task
        assigned_user_id: ID of the user being assigned
        assigned_by_id: ID of the user who made the assignment
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        db = get_db()
        
        # Get task details
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return False
        
        # Get assigned user details
        assigned_user = db.query(User).filter(User.id == assigned_user_id).first()
        if not assigned_user:
            logger.error(f"Assigned user {assigned_user_id} not found")
            return False
        
        # Get assigned by user details
        assigned_by_user = db.query(User).filter(User.id == assigned_by_id).first()
        if not assigned_by_user:
            logger.error(f"Assigned by user {assigned_by_id} not found")
            return False
        
        # Get project details
        project = db.query(Project).filter(Project.id == task.project_id).first()
        if not project:
            logger.error(f"Project {task.project_id} not found")
            return False
        
        # Send the email
        success = email_service.send_task_assignment_notification(
            task_title=task.title,
            project_title=project.title,
            assigned_user_email=assigned_user.email,
            assigned_user_name=assigned_user.name,
            assigned_by_name=assigned_by_user.name
        )
        
        if success:
            logger.info(f"Task assignment email sent successfully to {assigned_user.email}")
        else:
            logger.error(f"Failed to send task assignment email to {assigned_user.email}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error in send_task_assignment_email: {e}")
        # Retry the task with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)
    finally:
        db.close()

@shared_task(bind=True, max_retries=3)
def send_task_status_change_email(self, task_id: int, user_id: int, changed_by_id: int, 
                                old_status: str, new_status: str) -> bool:
    """
    Background task to send task status change notification email.
    
    Args:
        task_id: ID of the task that changed status
        user_id: ID of the user to notify
        changed_by_id: ID of the user who changed the status
        old_status: Previous status
        new_status: New status
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        db = get_db()
        
        # Get task details
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return False
        
        # Get user to notify
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        # Get user who made the change
        changed_by_user = db.query(User).filter(User.id == changed_by_id).first()
        if not changed_by_user:
            logger.error(f"Changed by user {changed_by_id} not found")
            return False
        
        # Get project details
        project = db.query(Project).filter(Project.id == task.project_id).first()
        if not project:
            logger.error(f"Project {task.project_id} not found")
            return False
        
        # Send the email
        success = email_service.send_task_status_change_notification(
            task_title=task.title,
            project_title=project.title,
            user_email=user.email,
            user_name=user.name,
            old_status=old_status,
            new_status=new_status,
            changed_by_name=changed_by_user.name
        )
        
        if success:
            logger.info(f"Task status change email sent successfully to {user.email}")
        else:
            logger.error(f"Failed to send task status change email to {user.email}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error in send_task_status_change_email: {e}")
        # Retry the task with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)
    finally:
        db.close()

@shared_task
def send_daily_overdue_summary() -> Dict[str, Any]:
    """
    Background task to send daily summary of overdue tasks to all users.
    This task runs automatically every 24 hours.
    
    Returns:
        Dict with summary of emails sent
    """
    try:
        db = get_db()
        today = datetime.now().date()
        
        # Get all users
        users = db.query(User).all()
        emails_sent = 0
        total_overdue_tasks = 0
        
        for user in users:
            # Get overdue tasks for this user (tasks they own or are assigned to)
            overdue_tasks = db.query(Task).join(Project).filter(
                (Project.owner_id == user.id) | (Task.assigned_user_id == user.id),
                Task.due_date < today,
                Task.status != 'done'  # Only include incomplete tasks
            ).all()
            
            if overdue_tasks:
                # Send summary email to this user
                success = send_overdue_summary_to_user.delay(user.id, [task.id for task in overdue_tasks])
                if success:
                    emails_sent += 1
                    total_overdue_tasks += len(overdue_tasks)
        
        logger.info(f"Daily overdue summary: {emails_sent} emails sent for {total_overdue_tasks} overdue tasks")
        
        return {
            "emails_sent": emails_sent,
            "total_overdue_tasks": total_overdue_tasks,
            "date": today.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in send_daily_overdue_summary: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@shared_task(bind=True, max_retries=3)
def send_overdue_summary_to_user(self, user_id: int, task_ids: List[int]) -> bool:
    """
    Send overdue task summary to a specific user.
    
    Args:
        user_id: ID of the user to send summary to
        task_ids: List of overdue task IDs
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        db = get_db()
        
        # Get user details
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        # Get task details
        tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
        if not tasks:
            logger.error(f"No tasks found for IDs: {task_ids}")
            return False
        
        # Create summary email content
        subject = f"Daily Summary: {len(tasks)} Overdue Tasks"
        
        # Group tasks by project
        tasks_by_project = {}
        for task in tasks:
            project = db.query(Project).filter(Project.id == task.project_id).first()
            if project:
                if project.title not in tasks_by_project:
                    tasks_by_project[project.title] = []
                tasks_by_project[project.title].append(task)
        
        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2>Daily Overdue Tasks Summary</h2>
            <p>Hello {user.name},</p>
            <p>You have {len(tasks)} overdue task(s) that need your attention:</p>
        """
        
        for project_title, project_tasks in tasks_by_project.items():
            html_content += f"""
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Project: {project_title}</h3>
                <ul>
            """
            for task in project_tasks:
                html_content += f"""
                    <li>
                        <strong>{task.title}</strong> - Due: {task.due_date.strftime('%B %d, %Y')}
                        <br><em>Status: {task.status.title()}, Priority: {task.priority.title()}</em>
                    </li>
                """
            html_content += """
                </ul>
            </div>
            """
        
        html_content += """
            <p>Please log in to your task management system to update these tasks.</p>
            <p>Best regards,<br>Task Management System</p>
        </body>
        </html>
        """
        
        # Send the email
        success = email_service.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content
        )
        
        if success:
            logger.info(f"Overdue summary email sent successfully to {user.email}")
        else:
            logger.error(f"Failed to send overdue summary email to {user.email}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error in send_overdue_summary_to_user: {e}")
        # Retry the task with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)
    finally:
        db.close()
