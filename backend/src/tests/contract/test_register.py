import pytest
from fastapi.testclient import TestClient
from ...main import app
from ...models.database import SessionLocal, Base, engine
from ...models.user import User as UserModel
from ...services.auth import hash_password

client = TestClient(app)


def test_register_new_user_returns_201():
    """Test that registering a new user returns 201 status code."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "user_id" in data
    assert "email" in data
    assert data["email"] == "newuser@example.com"
    assert "message" in data


def test_register_duplicate_email_returns_409():
    """Test that registering with an existing email returns 409 Conflict."""
    # Clean up any existing test user
    db = SessionLocal()
    db.query(UserModel).filter(UserModel.email == "duplicate@example.com").delete()
    db.commit()

    # First registration should succeed
    response1 = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123"
        }
    )
    assert response1.status_code == 201

    # Second registration with same email should fail
    response2 = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "AnotherPass456"
        }
    )
    assert response2.status_code == 409
    data = response2.json()
    assert "detail" in data


def test_register_invalid_email_returns_400():
    """Test that registering with invalid email format returns 400."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",
            "password": "SecurePass123"
        }
    )
    assert response.status_code == 400


def test_register_short_password_returns_400():
    """Test that registering with short password returns 400."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "valid@example.com",
            "password": "short"
        }
    )
    assert response.status_code == 400


def test_register_missing_fields_returns_400():
    """Test that registering with missing fields returns 400."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "valid@example.com"
            # password missing
        }
    )
    assert response.status_code == 400
