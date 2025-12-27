import pytest
from fastapi.testclient import TestClient
from ...main import app
from ...models.database import SessionLocal, Base
from ...models.user import User as UserModel

client = TestClient(app)


def test_signout_valid_session_returns_200():
    """Test that signing out with valid session returns 200 and clears cookie."""
    # Register and sign in first
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "signout@example.com",
            "password": "SecurePass123"
        }
    )
    assert register_response.status_code == 201

    signin_response = client.post(
        "/api/auth/sign-in",
        json={
            "email": "signout@example.com",
            "password": "SecurePass123"
        }
    )
    assert signin_response.status_code == 200

    # Get session cookie
    session_token = signin_response.cookies.get("session_token")
    assert session_token is not None

    # Sign out
    signout_response = client.post(
        "/api/auth/sign-out",
        cookies={"session_token": session_token}
    )
    assert signout_response.status_code == 200
    data = signout_response.json()
    assert "message" in data

    # Check that session cookie is cleared
    cookies = signout_response.cookies
    # Cookie should be cleared (Max-Age=0)
    assert "session_token" in cookies


def test_signout_no_session_returns_401():
    """Test that signing out without session returns 401."""
    response = client.post(
        "/api/auth/sign-out",
        cookies={"session_token": "invalid_token"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_signout_missing_cookie_returns_401():
    """Test that signing out without cookie returns 401."""
    response = client.post(
        "/api/auth/sign-out"
        # No cookies provided
    )
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
