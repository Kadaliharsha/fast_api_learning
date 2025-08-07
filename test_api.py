#!/usr/bin/env python3
"""
API Test Script for Task Management System
Tests all major endpoints and functionality
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.project_id = None
        self.task_id = None
        
    def print_result(self, test_name: str, success: bool, response: requests.Response = None):
        """Print test result with formatting"""
        if success:
            print(f"✅ {test_name}")
        else:
            print(f"❌ {test_name}")
            if response:
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
        print()
    
    def test_health_check(self) -> bool:
        """Test API health endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            success = response.status_code == 200
            self.print_result("Health Check", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Health Check", False)
            print(f"   Error: {e}")
            return False
    
    def test_register(self) -> bool:
        """Test user registration"""
        try:
            data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "testpassword123"
            }
            response = self.session.post(f"{BASE_URL}/register", json=data)
            success = response.status_code == 200
            self.print_result("User Registration", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("User Registration", False)
            print(f"   Error: {e}")
            return False
    
    def test_login(self) -> bool:
        """Test user login"""
        try:
            data = {
                "username": "test@example.com",
                "password": "testpassword123"
            }
            response = self.session.post(f"{BASE_URL}/login", data=data)
            success = response.status_code == 200
            if success:
                result = response.json()
                self.token = result.get("access_token")
                print(f"   Token received: {self.token[:20]}...")
            self.print_result("User Login", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("User Login", False)
            print(f"   Error: {e}")
            return False
    
    def test_create_project(self) -> bool:
        """Test project creation"""
        if not self.token:
            self.print_result("Create Project", False)
            print("   No authentication token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "title": "Test Project",
                "description": "A test project for API testing"
            }
            response = self.session.post(f"{BASE_URL}/projects/", json=data, headers=headers)
            success = response.status_code == 201
            if success:
                result = response.json()
                self.project_id = result.get("id")
                print(f"   Project created with ID: {self.project_id}")
            self.print_result("Create Project", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Create Project", False)
            print(f"   Error: {e}")
            return False
    
    def test_get_projects(self) -> bool:
        """Test getting user's projects"""
        if not self.token:
            self.print_result("Get Projects", False)
            print("   No authentication token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{BASE_URL}/projects/", headers=headers)
            success = response.status_code == 200
            if success:
                projects = response.json()
                print(f"   Found {len(projects)} project(s)")
            self.print_result("Get Projects", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Get Projects", False)
            print(f"   Error: {e}")
            return False
    
    def test_create_task(self) -> bool:
        """Test task creation"""
        if not self.token or not self.project_id:
            self.print_result("Create Task", False)
            print("   No authentication token or project ID available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "title": "Test Task",
                "description": "A test task for API testing",
                "project_id": self.project_id,
                "priority": "high",
                "status": "todo"
            }
            response = self.session.post(f"{BASE_URL}/tasks/", json=data, headers=headers)
            success = response.status_code == 200
            if success:
                result = response.json()
                self.task_id = result.get("id")
                print(f"   Task created with ID: {self.task_id}")
            self.print_result("Create Task", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Create Task", False)
            print(f"   Error: {e}")
            return False
    
    def test_get_tasks(self) -> bool:
        """Test getting tasks with filtering"""
        if not self.token:
            self.print_result("Get Tasks", False)
            print("   No authentication token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            params = {
                "status": "todo",
                "priority": "high",
                "limit": 10
            }
            response = self.session.get(f"{BASE_URL}/tasks/", headers=headers, params=params)
            success = response.status_code == 200
            if success:
                tasks = response.json()
                print(f"   Found {len(tasks)} task(s) with filters")
            self.print_result("Get Tasks (with filtering)", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Get Tasks (with filtering)", False)
            print(f"   Error: {e}")
            return False
    
    def test_update_task(self) -> bool:
        """Test task update"""
        if not self.token or not self.task_id:
            self.print_result("Update Task", False)
            print("   No authentication token or task ID available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "status": "in_progress",
                "description": "Updated task description"
            }
            response = self.session.patch(f"{BASE_URL}/tasks/{self.task_id}", json=data, headers=headers)
            success = response.status_code == 200
            if success:
                result = response.json()
                print(f"   Task updated: {result.get('title')} -> {result.get('status')}")
            self.print_result("Update Task", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Update Task", False)
            print(f"   Error: {e}")
            return False
    
    def test_get_task_details(self) -> bool:
        """Test getting specific task details"""
        if not self.token or not self.task_id:
            self.print_result("Get Task Details", False)
            print("   No authentication token or task ID available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{BASE_URL}/tasks/{self.task_id}", headers=headers)
            success = response.status_code == 200
            if success:
                task = response.json()
                print(f"   Task: {task.get('title')} (Status: {task.get('status')})")
            self.print_result("Get Task Details", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Get Task Details", False)
            print(f"   Error: {e}")
            return False
    
    def test_update_project(self) -> bool:
        """Test project update"""
        if not self.token or not self.project_id:
            self.print_result("Update Project", False)
            print("   No authentication token or project ID available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            data = {
                "title": "Updated Test Project",
                "description": "Updated project description"
            }
            response = self.session.patch(f"{BASE_URL}/projects/{self.project_id}", json=data, headers=headers)
            success = response.status_code == 200
            if success:
                result = response.json()
                print(f"   Project updated: {result.get('title')}")
            self.print_result("Update Project", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Update Project", False)
            print(f"   Error: {e}")
            return False
    
    def test_get_project_details(self) -> bool:
        """Test getting specific project details"""
        if not self.token or not self.project_id:
            self.print_result("Get Project Details", False)
            print("   No authentication token or project ID available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.session.get(f"{BASE_URL}/projects/{self.project_id}", headers=headers)
            success = response.status_code == 200
            if success:
                project = response.json()
                print(f"   Project: {project.get('title')} with {len(project.get('tasks', []))} task(s)")
            self.print_result("Get Project Details", success, response if not success else None)
            return success
        except Exception as e:
            self.print_result("Get Project Details", False)
            print(f"   Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting API Tests...")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_register),
            ("User Login", self.test_login),
            ("Create Project", self.test_create_project),
            ("Get Projects", self.test_get_projects),
            ("Create Task", self.test_create_task),
            ("Get Tasks (with filtering)", self.test_get_tasks),
            ("Update Task", self.test_update_task),
            ("Get Task Details", self.test_get_task_details),
            ("Update Project", self.test_update_project),
            ("Get Project Details", self.test_get_project_details),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                print(f"❌ {test_name} - Exception: {e}")
                print()
        
        print("=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")
        
        return passed == total

def main():
    """Main function to run the API tests"""
    print("🚀 Task Management System API Test Suite")
    print("Make sure the API is running on http://localhost:8000")
    print()
    
    tester = APITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ API is ready for use!")
        print("📖 View API documentation at: http://localhost:8000/docs")
    else:
        print("\n❌ API tests failed. Please check the application logs.")
        print("📋 View logs with: docker-compose logs api")

if __name__ == "__main__":
    main()
