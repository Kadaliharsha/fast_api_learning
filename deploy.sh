#!/bin/bash

# Task Management System API Deployment Script

echo "🚀 Starting Task Management System API..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env_template.txt .env
    echo "⚠️  Please edit .env file with your configuration before starting the application."
    echo "   Required: Database and Email settings"
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the application
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if API is running
echo "🔍 Checking API health..."
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ API is running successfully!"
    echo ""
    echo "🌐 Access your application:"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Alternative Docs:  http://localhost:8000/redoc"
    echo "   Health Check:      http://localhost:8000/"
    echo ""
    echo "📊 Services running:"
    echo "   - FastAPI (API): http://localhost:8000"
    echo "   - MySQL: localhost:3307"
    echo "   - Redis: localhost:6379"
    echo "   - Celery Worker: Background processing"
    echo "   - Celery Beat: Scheduled tasks"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Register a user: POST /register"
    echo "   2. Login: POST /login"
    echo "   3. Use the JWT token in Authorization header"
    echo "   4. Create projects and tasks"
    echo ""
    echo "📋 View logs: docker-compose logs -f"
    echo "🛑 Stop services: docker-compose down"
else
    echo "❌ API is not responding. Check logs with: docker-compose logs api"
    exit 1
fi
