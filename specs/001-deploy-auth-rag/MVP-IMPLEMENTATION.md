# MVP Implementation Guide: Backend Deployment & Auth Infrastructure

**Feature**: 001-deploy-auth-rag
**Scope**: Phase 1 + Phase 2 + Phase 3: User Story 1 (24 tasks total)
**Estimated Time**: 2-3 hours
**Goal**: Deploy RAG backend to Hugging Face Spaces with authentication token verification

---

## Overview

This guide implements the MVP scope - deploying the FastAPI backend to Hugging Face Spaces with:
- Health check endpoint
- Authentication middleware (token verification)
- Security headers
- CORS configuration
- Rate limiting
- Database schema initialization

### What's NOT in MVP

- User registration/sign-in (User Story 2)
- Chat interface (User Story 3)
- Frontend authentication components

---

## Pre-Requisites

1. **Hugging Face Account**: Sign up at https://huggingface.co (free tier)
2. **Neon Postgres Account**: Sign up at https://neon.tech (free tier)
3. **Python 3.11+**: Installed locally for development
4. **Git**: Configured for version control

---

## Phase 1: Setup (7 Tasks)

### Task 1: Backend Directory Structure ✅ (Done)

```bash
# Directory structure created:
backend/src/
├── models/
├── services/
├── api/
│   ├── routes/
│   └── middleware/
└── tests/
    ├── unit/
    ├── contract/
    └── integration/
```

### Task 2: Frontend Directory Structure ✅ (Done)

```bash
# Directory structure created:
frontend/src/
├── components/
│   ├── auth/
│   └── chat/
├── pages/
├── services/
├── lib/
└── tests/
```

### Task 3: Backend Requirements.txt ✅ (Done)

`backend/requirements.txt` contains:
- fastapi==0.109.0
- uvicorn[standard]==0.27.0
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9
- passlib[bcrypt]==1.7.4
- slowapi==0.1.9
- python-jose[cryptography]==3.3.0
- python-multipart==0.0.6
- pydantic==2.5.0
- pydantic-settings==2.1.0

### Task 4: Frontend Dependencies

Skip for MVP - frontend auth not needed for backend deployment.

### Task 5: Dockerfile ✅ (Done)

`backend/Dockerfile` created with:
- Python 3.11-slim base image
- Requirements installation
- Port 7860 exposed
- Uvicorn startup command

### Task 6: backend/.env.example ✅ (Done)

`backend/.env.example` created with placeholders:
- DATABASE_URL
- SECRET_KEY
- FRONTEND_URL

### Task 7: frontend/.env.local.example ✅ (Done)

`frontend/.env.local.example` created with:
- NEXT_PUBLIC_API_URL

---

## Phase 2: Foundational (10 Tasks) - BLOCKS User Stories

### Task 8: Database Schema

Create `backend/src/models/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require"
    SECRET_KEY: str = "your-secret-key-here"
    FRONTEND_URL: str = "https://your-app.vercel.app"

settings = Settings()

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database tables
def init_db():
    from .user import User
    from .session import Session
    Base.metadata.create_all(bind=engine)
```

### Task 9: User Model

Create `backend/src/models/user.py`:

```python
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())

    sessions = relationship("Session", back_populates="user")

import uuid
```

### Task 10: Session Model

Create `backend/src/models/session.py`:

```python
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)

    user = relationship("User", back_populates="sessions")

import uuid
```

### Task 11: Database Connection

Already created in Task 8 (`get_db()` function).

### Task 12: Authentication Services

Create `backend/src/services/auth.py`:

```python
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_session(db: Session, user_id: str, ip_address: str = None, user_agent: str = None) -> dict:
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    from ..models.session import Session as SessionModel
    session = SessionModel(
        user_id=user_id,
        session_token=session_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "id": session.id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat()
    }

def verify_session(db: Session, session_token: str):
    from ..models.session import Session as SessionModel
    from ..models.user import User

    session = db.query(SessionModel).filter(
        SessionModel.session_token == session_token,
        SessionModel.expires_at > datetime.utcnow()
    ).first()

    if not session:
        return None

    user = db.query(User).filter(User.id == session.user_id).first()
    return user
```

### Task 13: Main FastAPI Application

Create `backend/src/main.py`:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .models.database import settings, init_db
from .api.routes import health

app = FastAPI(title="Authenticated RAG Backend")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Include routes
app.include_router(health.router, tags=["Health"])

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

### Task 14: Security Headers Middleware

Already integrated in Task 13 (`add_security_headers` middleware).

### Task 15: Rate Limiting

Create `backend/src/api/middleware/rate_limit.py`:

```python
from slowapi import Limiter, get_remote_address
from slowapi.util import get_ipaddr
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, Request

limiter = Limiter(key_func=get_remote_address)
slow = Limiter(key_func=get_ipaddr, default_limits=["10/minute"])

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded. Please wait {exc.retry_after} seconds.",
        headers={"Retry-After": str(exc.retry_after)},
    )
```

### Task 16: Logging Configuration

Create `backend/src/api/middleware/logging.py`:

```python
import logging
import json
from datetime import datetime
from fastapi import Request
from typing import Callable

logger = logging.getLogger(__name__)

class StructuredLogger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )

    def log_auth_event(self, event_type: str, user_id: str, **kwargs):
        log_entry = {
            "event": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(json.dumps(log_entry))

    def log_error(self, error_type: str, error_message: str, **kwargs):
        log_entry = {
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.error(json.dumps(log_entry))

structured_logger = StructuredLogger()
```

### Task 17: Authentication Middleware

Create `backend/src/api/middleware/auth.py`:

```python
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ...services.auth import verify_session
from ...models.database import get_db

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Skip auth for auth endpoints (not in MVP but future-proof)
        if "/api/auth/" in request.url.path:
            return await call_next(request)

        # Extract session token from cookie
        session_token = request.cookies.get("session_token")

        if not session_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )

        # Verify session
        from ...models.database import get_db
        db = next(get_db())
        user = verify_session(db, session_token)

        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired session"}
            )

        # Add user to request state
        request.state.user = user

        return await call_next(request)
```

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Backend Deployment & Token Verification (10 Tasks) 🎯 MVP

### Tests (Write FIRST - should FAIL)

#### Task 18: Health Check Contract Test

Create `backend/src/tests/contract/test_health.py`:

```python
import pytest
from fastapi.testclient import TestClient
from ...main import app

client = TestClient(app)

def test_health_check_returns_200():
    response = client.get("/health")
    assert response.status_code == 200

def test_health_check_returns_correct_structure():
    response = client.get("/health")
    assert "status" in response.json()
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()
```

#### Task 19: Token Verification Middleware Test

Create `backend/src/tests/unit/test_auth_middleware.py`:

```python
import pytest
from fastapi import Request
from ...api.middleware.auth import AuthMiddleware
from unittest.mock import Mock, patch

def test_missing_token_returns_401():
    request = Mock(spec=Request)
    request.cookies = {}
    request.url = Mock(path="/api/chat/message")

    middleware = AuthMiddleware(app)

    with patch.object(middleware, 'call_next') as mock_call_next:
        mock_call_next.return_value = Mock()
        result = middleware.dispatch(request, mock_call_next)

        assert result.status_code == 401

def test_invalid_token_returns_401():
    request = Mock(spec=Request)
    request.cookies = {"session_token": "invalid_token"}
    request.url = Mock(path="/api/chat/message")

    middleware = AuthMiddleware(app)

    with patch.object(middleware, 'call_next') as mock_call_next:
        with patch('...services.auth.verify_session', return_value=None):
            mock_call_next.return_value = Mock()
            result = middleware.dispatch(request, mock_call_next)

            assert result.status_code == 401
```

### Implementation

#### Task 20: Health Check Endpoint

Already implemented in Task 13 (`/health` endpoint).

#### Task 21: Integrate Authentication Middleware

Update `backend/src/main.py` to include AuthMiddleware:

```python
from .api.middleware.auth import AuthMiddleware

app = FastAPI(title="Authenticated RAG Backend")
app.add_middleware(AuthMiddleware, app)
```

#### Task 22: Add Security Headers

Already integrated in Task 13.

#### Task 23: Configure CORS

Already configured in Task 13.

#### Task 24: Add Rate Limiting

Update `backend/src/main.py` to include rate limiting:

```python
from .api.middleware.rate_limit import limiter, slow

@app.get("/health")
@slow
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
```

#### Task 25: Configure Logging

Update `backend/src/main.py` to initialize logging:

```python
from .api.middleware.logging import structured_logger

# On startup
@app.on_event("startup")
def startup_event():
    init_db()
    structured_logger.log_error("info", "Application started", message="Backend service initialized")
```

#### Task 26: Update Dockerfile

Already created in Task 5.

#### Task 27: Database Schema Initialization

Update `backend/src/models/database.py` with complete schema:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, ForeignKey
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require"
    SECRET_KEY: str = "your-secret-key-here"
    FRONTEND_URL: str = "https://your-app.vercel.app"

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

# Models
import uuid
from datetime import datetime, timedelta

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, server_default=datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
```

**Checkpoint**: User Story 1 complete - backend deployed with auth infrastructure

---

## Deployment to Hugging Face Spaces

### 1. Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Name: `rag-auth-backend`
3. License: MIT
4. Space SDK: Docker
5. Visibility: Public (or Private for MVP)

### 2. Clone Space Locally

```bash
git clone https://huggingface.co/spaces/your-username/rag-auth-backend
cd rag-auth-backend
```

### 3. Copy Backend Files

Copy all backend files to the space repository:
- `backend/src/` (all files)
- `backend/requirements.txt`
- `backend/Dockerfile`

### 4. Configure Environment Variables

In Hugging Face Space Settings → Variables:
```
DATABASE_URL=postgresql://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=your-generated-secret-key-here
FRONTEND_URL=https://your-app.vercel.app
```

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Commit and Push

```bash
git add .
git commit -m "Deploy authenticated RAG backend with auth middleware"
git push
```

### 6. Verify Deployment

1. Wait 5-10 minutes for Hugging Face to build
2. Open: `https://huggingface.co/spaces/your-username/rag-auth-backend`
3. Test health endpoint: Click "Open in new tab"
4. Should see: `{"status":"healthy","timestamp":"..."}`

---

## Testing MVP

### Test 1: Health Check (Public)

```bash
curl https://huggingface.co/spaces/your-username/rag-auth-backend/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T12:00:00Z"
}
```

### Test 2: Unauthenticated Request (Protected)

```bash
curl https://huggingface.co/spaces/your-username/rag-auth-backend/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

Expected response: `401 Unauthorized` (with or without cookie)

### Test 3: Authenticated Request (Will fail - no session yet)

```bash
curl https://huggingface.co/spaces/your-username/rag-auth-backend/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=test" \
  -d '{"message":"test"}'
```

Expected response: `401 Unauthorized` (invalid token)

---

## Validation Checklist

- [ ] Backend directory structure created (T001)
- [ ] Frontend directory structure created (T002)
- [ ] backend/requirements.txt with all dependencies (T003)
- [ ] backend/Dockerfile created for Hugging Face Spaces (T005)
- [ ] backend/.env.example with placeholders (T006)
- [ ] frontend/.env.local.example created (T007)
- [ ] Database schema with User and Session models (T008, T009, T010)
- [ ] Database connection and session management (T011)
- [ ] Authentication service utilities (T012)
- [ ] Main FastAPI application with CORS (T013)
- [ ] Security headers middleware (T014)
- [ ] Rate limiting configuration (T015)
- [ ] Structured logging configuration (T016)
- [ ] Authentication middleware for token verification (T017)
- [ ] Health check contract tests written (T018)
- [ ] Token verification middleware tests written (T019)
- [ ] Health check endpoint implemented (T020)
- [ ] Authentication middleware integrated (T021)
- [ ] Security headers added (T022)
- [ ] CORS configured (T023)
- [ ] Rate limiting added (T024)
- [ ] Structured logging configured (T025)
- [ ] Dockerfile verified (T026)
- [ ] Database schema initialization added (T027)
- [ ] Backend deployed to Hugging Face Spaces
- [ ] Health endpoint accessible via HTTPS
- [ ] Unauthenticated requests return 401
- [ ] All tests pass

---

## Next Steps (After MVP)

### User Story 2: Registration & Sign-In (23 tasks)

Add:
- User registration endpoint (`POST /api/auth/register`)
- User sign-in endpoint (`POST /api/auth/sign-in`)
- User sign-out endpoint (`POST /api/auth/sign-out`)
- Password hashing and verification
- Session creation and management
- Frontend sign-in/sign-up forms

### User Story 3: Authenticated Chat Interface (19 tasks)

Add:
- Protected chat endpoint (`POST /api/chat/message`)
- Rate limiting for chat
- Frontend ChatInterface component
- Frontend protected chat page
- Message transmission and display

---

## Troubleshooting

### Issue: Hugging Face Build Fails

**Check**:
- Dockerfile syntax is correct
- requirements.txt has no invalid packages
- All Python files have proper imports

**Solution**: Check Hugging Face Space logs for error messages

### Issue: 401 Unauthorized for all requests

**Check**:
- SECRET_KEY environment variable is set
- Database tables are created
- Session token is being sent in cookie

**Solution**: Verify middleware is correctly integrated

### Issue: CORS errors in browser

**Check**:
- FRONTEND_URL environment variable matches your Vercel URL
- `allow_credentials=True` is set in CORS config
- Cookie attributes (httpOnly, secure, SameSite) are correct

**Solution**: Update FRONTEND_URL and redeploy

---

## References

- [Tasks.md](../tasks.md) - Complete task breakdown
- [Data Model](../data-model.md) - Entity definitions
- [Backend API Contract](../contracts/backend-api.yaml) - OpenAPI spec
- [Auth Flows](../contracts/auth-flows.md) - Authentication documentation
- [Research](../research.md) - Technical decisions
- [Quickstart](../quickstart.md) - Step-by-step guide
