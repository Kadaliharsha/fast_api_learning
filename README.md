# Task Management System API

A lightweight, production-ready Task Management System built with FastAPI, featuring user authentication, project/task management, email notifications, and background job processing.

## 🚀 Features

### Core Functionality
- **User Authentication**: JWT-based authentication with secure password hashing
- **Project Management**: Create, read, update, and delete projects
- **Task Management**: Full CRUD operations with filtering, sorting, and pagination
- **Authorization**: Users can only access their own projects and assigned tasks

### Advanced Features
- **Email Notifications**: Automatic email notifications for task assignments and status changes
- **Background Processing**: Celery worker for asynchronous email sending
- **Daily Summaries**: Automated daily emails for overdue tasks
- **Filtering & Pagination**: Advanced task filtering by status, priority, due date, and project

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: MySQL 8.0
- **Cache/Message Broker**: Redis 7
- **Background Jobs**: Celery
- **Authentication**: JWT tokens
- **Email**: SMTP (Gmail, SendGrid, etc.)
- **Containerization**: Docker & Docker Compose

## 📋 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login (returns JWT token)

### Projects
- `POST /projects/` - Create a new project
- `GET /projects/` - List all projects for current user
- `GET /projects/{id}` - Get project details with all tasks
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Tasks
- `POST /tasks/` - Create a new task
- `GET /tasks/` - List tasks with filtering, sorting, pagination
- `GET /tasks/{id}` - Get task details
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Task Filtering & Sorting
- **Filters**: `status`, `priority`, `due_date`, `project_id`
- **Sorting**: `priority`, `due_date`
- **Pagination**: `limit`, `offset`

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Clone and Setup
```bash
git clone <repository-url>
cd task-management-api
```

### 2. Environment Configuration
```bash
# Copy environment template
cp env_template.txt .env

# Edit .env with your settings
# Required: Database and Email configuration
```

### 3. Start the Application
```bash
# Start all services (API, MySQL, Redis, Celery workers)
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### 4. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env_template.txt`:

```env
# Database Configuration
DB_USER=root
DB_PASSWORD=123456
DB_HOST=localhost
DB_NAME=task_manager
DB_PORT=3307

# Email Configuration (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# JWT Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### Email Setup

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in `EMAIL_PASSWORD`

## 📊 Database Schema

### Users
- `id` (Primary Key)
- `name` (String)
- `email` (Unique, String)
- `hashed_password` (String)

### Projects
- `id` (Primary Key)
- `title` (String)
- `description` (String)
- `owner_id` (Foreign Key to Users)

### Tasks
- `id` (Primary Key)
- `title` (String)
- `description` (String)
- `status` (Enum: todo, in_progress, done)
- `priority` (Enum: low, medium, high)
- `due_date` (DateTime)
- `project_id` (Foreign Key to Projects)
- `assigned_user_id` (Foreign Key to Users)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## 🔄 Background Jobs

### Celery Workers
The application includes two Celery services:

1. **Celery Worker**: Processes email notifications
2. **Celery Beat**: Schedules daily overdue task summaries

### Email Notifications
- **Task Assignment**: Sent when a task is assigned to a user
- **Status Change**: Sent when a task's status is updated
- **Daily Summary**: Daily email with overdue tasks

## 🧪 Testing

### Manual Testing
```bash
# Test database connection
python test_db.py

# Check users
python check_users.py
```

### API Testing
1. Register a user: `POST /register`
2. Login: `POST /login`
3. Use the JWT token in Authorization header: `Bearer <token>`
4. Create projects and tasks
5. Test filtering and notifications

## 🐳 Docker Services

The application runs with 5 services:

1. **api**: FastAPI application (port 8000)
2. **mysql**: MySQL database (port 3307)
3. **redis**: Redis cache/broker (port 6379)
4. **celery_worker**: Background job processor
5. **celery_beat**: Scheduled task scheduler

## 📈 Monitoring

### Health Checks
- API: `GET /` (returns welcome message)
- Database: Connection tested on startup
- Celery: Workers automatically restart on failure

### Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs api
docker-compose logs celery_worker
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt for password security
- **Authorization**: Users can only access their own data
- **Input Validation**: Pydantic schemas for request validation
- **SQL Injection Protection**: SQLAlchemy ORM

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Use proper secrets management
2. **Database**: Use managed MySQL service
3. **Redis**: Use managed Redis service
4. **Email**: Configure production SMTP or email service
5. **SSL/TLS**: Add reverse proxy with HTTPS
6. **Monitoring**: Add application monitoring

### Scaling
- **Horizontal Scaling**: Run multiple API containers behind a load balancer
- **Database**: Use read replicas for read-heavy workloads
- **Redis**: Use Redis Cluster for high availability
- **Celery**: Scale workers based on queue size

## 📝 API Examples

### Register User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john@example.com&password=securepassword"
```

### Create Project
```bash
curl -X POST "http://localhost:8000/projects/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Project",
    "description": "A sample project"
  }'
```

### Create Task
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Task",
    "description": "A sample task",
    "project_id": 1,
    "priority": "high",
    "due_date": "2024-12-31T23:59:59"
  }'
```

### Filter Tasks
```bash
curl -X GET "http://localhost:8000/tasks/?status=todo&priority=high&limit=10" \
  -H "Authorization: Bearer <your_jwt_token>"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify environment configuration
3. Test database connection: `python test_db.py`
4. Check API documentation: http://localhost:8000/docs