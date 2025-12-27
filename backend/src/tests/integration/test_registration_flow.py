import pytest
from fastapi.testclient import TestClient
from ...main import app
from ...models.database import SessionLocal
from ...models.user import User as UserModel
from ...models.session import Session as SessionModel

client = TestClient(app)


def test_registration_flow_register_to_signin():
    """Test complete flow: register → verify in database → sign-in → verify session created."""
    # Clean up test user
    db = SessionLocal()
    db.query(UserModel).filter(UserModel.email == "flow@example.com").delete()
    db.query(SessionModel).filter(SessionModel.user_id != None).delete()
    db.commit()

    # Step 1: Register new user
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "flow@example.com",
            "password": "SecurePass123"
        }
    )
    assert register_response.status_code == 201
    register_data = register_response.json()
    user_id = register_data["user_id"]
    assert user_id is not None

    # Step 2: Verify user exists in database
    db = SessionLocal()
    user = db.query(UserModel).filter(UserModel.email == "flow@example.com").first()
    assert user is not None
    assert user.email == "flow@example.com"
    assert user.id == user_id

    # Step 3: Sign in
    signin_response = client.post(
        "/api/auth/sign-in",
        json={
            "email": "flow@example.com",
            "password": "SecurePass123"
        }
    )
    assert signin_response.status_code == 200
    signin_data = signin_response.json()
    assert signin_data["email"] == "flow@example.com"

    # Step 4: Verify session was created in database
    db = SessionLocal()
    sessions = db.query(SessionModel).filter(SessionModel.user_id == user_id).all()
    assert len(sessions) > 0
    latest_session = sessions[-1]
    assert latest_session.session_token is not None

    # Cleanup
    db.query(UserModel).filter(UserModel.email == "flow@example.com").delete()
    db.commit()
    db.close()


def test_registration_flow_password_hashing():
    """Test that password is properly hashed and not stored in plain text."""
    # Clean up test user
    db = SessionLocal()
    db.query(UserModel).filter(UserModel.email == "hash@example.com").delete()
    db.commit()

    # Register user
    plain_password = "SecurePass123"
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "hash@example.com",
            "password": plain_password
        }
    )
    assert register_response.status_code == 201

    # Verify password is hashed in database
    db = SessionLocal()
    user = db.query(UserModel).filter(UserModel.email == "hash@example.com").first()
    assert user is not None
    assert user.password_hash != plain_password
    # Hashed password should start with bcrypt format ($2b$)
    assert user.password_hash.startswith("$2b$")

    # Cleanup
    db.query(UserModel).filter(UserModel.email == "hash@example.com").delete()
    db.commit()
    db.close()


def test_registration_flow_session_expiration():
    """Test that sessions have proper expiration time (7 days)."""
    from datetime import datetime, timedelta

    # Clean up test user
    db = SessionLocal()
    db.query(UserModel).filter(UserModel.email == "expire@example.com").delete()
    db.query(SessionModel).filter(SessionModel.user_id != None).delete()
    db.commit()

    # Register and sign in
    client.post(
        "/api/auth/register",
        json={
            "email": "expire@example.com",
            "password": "SecurePass123"
        }
    )

    signin_response = client.post(
        "/api/auth/sign-in",
        json={
            "email": "expire@example.com",
            "password": "SecurePass123"
        }
    )
    assert signin_response.status_code == 200

    # Verify session expiration
    db = SessionLocal()
    session = db.query(SessionModel).first()
    assert session is not None

    # Check that expires_at is approximately 7 days from now
    expected_expiry = datetime.utcnow() + timedelta(days=7)
    time_diff = abs((session.expires_at - expected_expiry).total_seconds())
    # Allow 1 minute tolerance
    assert time_diff < 60

    # Cleanup
    db.query(UserModel).filter(UserModel.email == "expire@example.com").delete()
    db.commit()
    db.close()
