import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailService:
    """
    Email service for sending notifications about task updates.
    
    This service handles:
    - Task assignment notifications
    - Task status change notifications
    - Daily summary emails (for future use with Celery)
    """
    
    def __init__(self):
        """
        Initialize the email service with SMTP configuration.
        
        Reads email settings from environment variables:
        - EMAIL_HOST: SMTP server (e.g., 'smtp.gmail.com')
        - EMAIL_PORT: SMTP port (e.g., 587 for TLS)
        - EMAIL_USER: Email username
        - EMAIL_PASSWORD: Email password
        - EMAIL_FROM: Sender email address
        """
        # SMTP Configuration from environment variables
        self.smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM", self.email_user)
        
        # Validate that required email settings are provided
        if not all([self.email_user, self.email_password]):
            print("Warning: Email credentials not configured. Email notifications will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Send an email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML version of the email body
            text_content: Plain text version of the email body (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.enabled:
            print(f"Email disabled. Would have sent to {to_email}: {subject}")
            return False
        
        try:
            # Create the email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add both HTML and text versions
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Enable TLS encryption
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_task_assignment_notification(self, task_title: str, project_title: str, 
                                        assigned_user_email: str, assigned_user_name: str,
                                        assigned_by_name: str) -> bool:
        """
        Send notification when a task is assigned to a user.
        
        Args:
            task_title: Title of the assigned task
            project_title: Title of the project containing the task
            assigned_user_email: Email of the user being assigned
            assigned_user_name: Name of the user being assigned
            assigned_by_name: Name of the user who made the assignment
        
        Returns:
            bool: True if email sent successfully
        """
        subject = f"New Task Assigned: {task_title}"
        
        # HTML template for task assignment notification
        html_content = f"""
        <html>
        <body>
            <h2>You have been assigned a new task!</h2>
            <p>Hello {assigned_user_name},</p>
            <p>You have been assigned a new task by {assigned_by_name}.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Task Details:</h3>
                <p><strong>Task:</strong> {task_title}</p>
                <p><strong>Project:</strong> {project_title}</p>
                <p><strong>Assigned by:</strong> {assigned_by_name}</p>
                <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <p>Please log in to your task management system to view the full details and update the task status.</p>
            
            <p>Best regards,<br>Task Management System</p>
        </body>
        </html>
        """
        
        # Plain text version for email clients that don't support HTML
        text_content = f"""
        You have been assigned a new task!
        
        Hello {assigned_user_name},
        
        You have been assigned a new task by {assigned_by_name}.
        
        Task Details:
        - Task: {task_title}
        - Project: {project_title}
        - Assigned by: {assigned_by_name}
        - Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        Please log in to your task management system to view the full details and update the task status.
        
        Best regards,
        Task Management System
        """
        
        return self.send_email(assigned_user_email, subject, html_content, text_content)
    
    def send_task_status_change_notification(self, task_title: str, project_title: str,
                                           user_email: str, user_name: str,
                                           old_status: str, new_status: str,
                                           changed_by_name: str) -> bool:
        """
        Send notification when a task's status changes.
        
        Args:
            task_title: Title of the task
            project_title: Title of the project containing the task
            user_email: Email of the user to notify
            user_name: Name of the user to notify
            old_status: Previous status of the task
            new_status: New status of the task
            changed_by_name: Name of the user who changed the status
        
        Returns:
            bool: True if email sent successfully
        """
        subject = f"Task Status Updated: {task_title}"
        
        # HTML template for status change notification
        html_content = f"""
        <html>
        <body>
            <h2>Task Status Updated</h2>
            <p>Hello {user_name},</p>
            <p>A task's status has been updated by {changed_by_name}.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>Task Details:</h3>
                <p><strong>Task:</strong> {task_title}</p>
                <p><strong>Project:</strong> {project_title}</p>
                <p><strong>Status Changed:</strong> {old_status.title()} → {new_status.title()}</p>
                <p><strong>Changed by:</strong> {changed_by_name}</p>
                <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <p>Please log in to your task management system to view the updated task details.</p>
            
            <p>Best regards,<br>Task Management System</p>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        Task Status Updated
        
        Hello {user_name},
        
        A task's status has been updated by {changed_by_name}.
        
        Task Details:
        - Task: {task_title}
        - Project: {project_title}
        - Status Changed: {old_status.title()} → {new_status.title()}
        - Changed by: {changed_by_name}
        - Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        
        Please log in to your task management system to view the updated task details.
        
        Best regards,
        Task Management System
        """
        
        return self.send_email(user_email, subject, html_content, text_content)

# Create a global instance of the email service
email_service = EmailService()
