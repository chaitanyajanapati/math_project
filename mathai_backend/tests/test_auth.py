"""Test authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "grade": 8
        }
    )
    assert response.status_code == 201 or response.status_code == 400  # 400 if already exists
    if response.status_code == 201:
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "hashed_password" not in data


def test_login():
    """Test user login."""
    # First register
    client.post(
        "/api/auth/register",
        json={
            "email": "logintest@example.com",
            "username": "logintest",
            "password": "password123",
            "grade": 8
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        data={
            "username": "logintest@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info."""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "currentuser@example.com",
            "username": "currentuser",
            "password": "password123",
            "grade": 8
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "currentuser@example.com",
            "password": "password123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "currentuser@example.com"


def test_register_duplicate_email():
    """Test registering with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "password123",
        "grade": 8
    }
    
    # First registration
    client.post("/api/auth/register", json=user_data)
    
    # Second registration with same email
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400


def test_register_invalid_grade():
    """Test registering with invalid grade."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalidgrade@example.com",
            "username": "invalidgrade",
            "password": "password123",
            "grade": 15  # Invalid grade
        }
    )
    assert response.status_code == 422  # Validation error
