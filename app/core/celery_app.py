import os
from celery import Celery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Celery instance
# The first argument is the name of the current module
# The second argument is the broker URL (Redis in our case)
celery_app = Celery(
    "task_management",  # Application name
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),  # Message broker (Redis)
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),  # Result backend (Redis)
    # include=['app.tasks.email_tasks']  # Modules containing task definitions - temporarily disabled
)

# Celery configuration
celery_app.conf.update(
    # Task serialization format
    task_serializer='json',
    
    # Result serialization format
    result_serializer='json',
    
    # Accept content types
    accept_content=['json'],
    
    # Time zone
    timezone='UTC',
    
    # Enable UTC
    enable_utc=True,
    
    # Task routing (optional - for more complex setups)
    # task_routes={
    #     'app.tasks.email_tasks.*': {'queue': 'email_queue'},
    # },
    
    # Task execution settings
    task_always_eager=False,  # Set to True for testing (runs tasks synchronously)
    
    # Worker settings
    worker_prefetch_multiplier=1,
    
    # Task time limits
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    
    # Retry settings
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
)

# Optional: Configure periodic tasks (for daily summaries)
# celery_app.conf.beat_schedule = {
#     'send-daily-overdue-summary': {
#         'task': 'app.tasks.email_tasks.send_daily_overdue_summary',
#         'schedule': 86400.0,  # Run every 24 hours (in seconds)
#     },
# }

if __name__ == '__main__':
    celery_app.start()
