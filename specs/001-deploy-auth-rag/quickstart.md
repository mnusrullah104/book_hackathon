# Quickstart: Deploy Authenticated RAG Backend and UI

**Feature**: [001-deploy-auth-rag](../spec.md)
**Branch**: `001-deploy-auth-rag`
**Estimated Time**: 2-4 hours (depending on existing codebase)

## Prerequisites

- Hugging Face account (free tier)
- Vercel account (free tier)
- Neon Postgres account (free tier)
- Python 3.11+ installed locally
- Node.js 18+ installed locally
- Git configured

---

## Step 1: Set Up Database (Neon Postgres)

1. Create account at https://neon.tech (free tier)
2. Create new project: `rag-auth-db`
3. Get connection string:
   ```
   postgresql://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require
   ```
4. Save connection string as environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require"
   ```

---

## Step 2: Configure Backend (FastAPI)

### 2.1 Install Dependencies

```bash
cd backend
pip install fastapi uvicorn sqlalchemy psycopg2-binary bcrypt slowapi python-multipart python-jose
```

### 2.2 Create Database Models

Create `backend/src/models/user.py`:

```python
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())
```

Create `backend/src/models/session.py`:

```python
from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from .user import Base

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
```

### 2.3 Create Authentication Service

Create `backend/src/services/auth.py`:

```python
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.session import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_session(db: Session, user: User, ip_address: str = None, user_agent: str = None) -> Session:
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    session = Session(
        user_id=user.id,
        session_token=session_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def verify_session(db: Session, session_token: str) -> User | None:
    session = db.query(Session).filter(
        Session.session_token == session_token,
        Session.expires_at > datetime.utcnow()
    ).first()
    if not session:
        return None
    return session.user
```

### 2.4 Create API Routes

Create `backend/src/api/routes/auth.py`:

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ...services.auth import hash_password, verify_password, create_session, verify_session
from ...models.user import User
from ...database import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already in use")

    # Create user
    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"user_id": user.id, "email": user.email, "message": "Account created successfully"}

@router.post("/sign-in")
def sign_in(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create session
    session = create_session(db, user)

    # Return response (session cookie set by middleware)
    return {"user_id": user.id, "email": user.email, "message": "Signed in successfully"}

@router.post("/sign-out")
def sign_out(db: Session = Depends(get_db)):
    # Session token from cookie, delete session
    # Implementation depends on middleware extraction
    return {"message": "Signed out successfully"}
```

### 2.5 Create Main Application

Create `backend/src/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import auth, chat

app = FastAPI(title="Authenticated RAG Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],  # Replace with your Vercel URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Routes
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
```

---

## Step 3: Create Dockerfile for Hugging Face Spaces

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 7860

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

Create `backend/requirements.txt`:

```text
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
```

---

## Step 4: Deploy Backend to Hugging Face Spaces

1. Create new Space at https://huggingface.co/new-space
2. Choose:
   - Space name: `rag-auth-backend`
   - License: MIT
   - Space SDK: Docker
3. Clone the space locally:
   ```bash
   git clone https://huggingface.co/spaces/your-username/rag-auth-backend
   cd rag-auth-backend
   ```
4. Copy backend code to space repository
5. Add `.env` file (do NOT commit, use Hugging Face Secrets):
   ```bash
   DATABASE_URL=postgresql://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require
   SECRET_KEY=your-secret-key-here
   FRONTEND_URL=https://your-app.vercel.app
   ```
6. Add, commit, and push:
   ```bash
   git add .
   git commit -m "Deploy authenticated RAG backend"
   git push
   ```
7. Wait for Hugging Face to build and deploy (5-10 minutes)
8. Verify deployment: Open `https://huggingface.co/spaces/your-username/rag-auth-backend`
   - Should see: `{"status":"healthy","timestamp":"..."}`

---

## Step 5: Configure Frontend (Next.js)

### 5.1 Install Better Auth

```bash
cd frontend
npm install better-auth @auth/core
```

### 5.2 Configure Better Auth Client

Create `frontend/src/lib/auth.ts`:

```typescript
import { createAuthClient } from 'better-auth/react'

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://your-space.hf.space',
  credentials: 'include',
})

export type Session = Awaited<ReturnType<typeof authClient.getSession>>
```

### 5.3 Create Sign-In Page

Create `frontend/src/app/sign-in/page.tsx`:

```typescript
'use client'

import { useState } from 'react'
import { authClient } from '@/lib/auth'
import { useRouter } from 'next/navigation'

export default function SignInPage() {
  const router = useRouter()
  const [error, setError] = useState<string>()
  const [loading, setLoading] = useState(false)

  async function signIn(formData: FormData) {
    setError(undefined)
    setLoading(true)

    const email = formData.get('email') as string
    const password = formData.get('password') as string

    try {
      const result = await authClient.signIn.email({
        email,
        password,
      })

      if (result.error) {
        setError(result.error.message || 'Sign in failed')
        return
      }

      router.push('/chat')
    } catch (err) {
      setError('An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8">
        <h1 className="text-3xl font-bold">Sign In</h1>
        <form action={signIn} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              minLength={8}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          {error && <div className="text-red-500">{error}</div>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="text-center text-sm">
          Don't have an account?{' '}
          <a href="/sign-up" className="text-blue-600 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  )
}
```

### 5.4 Create Sign-Up Page

Create `frontend/src/app/sign-up/page.tsx`:

```typescript
'use client'

import { useState } from 'react'
import { authClient } from '@/lib/auth'
import { useRouter } from 'next/navigation'

export default function SignUpPage() {
  const router = useRouter()
  const [error, setError] = useState<string>()
  const [loading, setLoading] = useState(false)

  async function signUp(formData: FormData) {
    setError(undefined)
    setLoading(true)

    const email = formData.get('email') as string
    const password = formData.get('password') as string

    try {
      const result = await authClient.signUp.email({
        email,
        password,
      })

      if (result.error) {
        setError(result.error.message || 'Sign up failed')
        return
      }

      router.push('/sign-in')
    } catch (err) {
      setError('An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8">
        <h1 className="text-3xl font-bold">Create Account</h1>
        <form action={signUp} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium">
              Password (min 8 characters)
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              minLength={8}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          {error && <div className="text-red-500">{error}</div>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center text-sm">
          Already have an account?{' '}
          <a href="/sign-in" className="text-blue-600 hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </div>
  )
}
```

### 5.5 Create Protected Chat Page

Create `frontend/src/app/chat/page.tsx`:

```typescript
import { authClient } from '@/lib/auth'
import { redirect } from 'next/navigation'

export default async function ChatPage() {
  const session = await authClient.getSession()

  if (!session) {
    redirect('/sign-in')
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Chat</h1>
          <div className="flex items-center gap-4">
            <span>{session.user.email}</span>
            <button
              onClick={() => authClient.signOut()}
              className="px-4 py-2 border rounded"
            >
              Sign Out
            </button>
          </div>
        </header>
        <ChatInterface />
      </div>
    </div>
  )
}
```

### 5.6 Configure Environment Variables

Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://your-space.hf.space
```

---

## Step 6: Deploy Frontend to Vercel (if not already deployed)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Deploy:
   ```bash
   cd frontend
   vercel
   ```
3. Follow prompts:
   - Link to existing project or create new
   - Set environment variables (NEXT_PUBLIC_API_URL)
4. Wait for deployment (2-3 minutes)
5. Verify deployment: Open the Vercel URL

---

## Step 7: Test End-to-End Flow

1. **Navigate to sign-up page**: Open your Vercel URL + `/sign-up`
2. **Create account**: Enter email and password
3. **Sign in**: Enter credentials
4. **Access chat**: Should be redirected to `/chat`
5. **Send message**: Test chat functionality
6. **Verify session**: Refresh page, should remain signed in
7. **Sign out**: Click sign out, should be redirected to sign-in

---

## Troubleshooting

### Issue: CORS errors in browser console

**Solution**:
1. Check backend CORS configuration includes your Vercel URL
2. Verify `allow_credentials=True` is set
3. Check browser DevTools > Network > Headers

### Issue: Session cookie not being sent

**Solution**:
1. Verify frontend uses `credentials: 'include'`
2. Check both backend and frontend use HTTPS
3. Inspect cookies in browser DevTools > Application > Cookies

### Issue: Backend deployment fails on Hugging Face

**Solution**:
1. Check Hugging Face Spaces logs for build errors
2. Verify Dockerfile COPY paths are correct
3. Ensure dependencies are in requirements.txt

### Issue: Database connection errors

**Solution**:
1. Verify DATABASE_URL environment variable is set in Hugging Face Secrets
2. Check Neon database is active (not paused)
3. Test connection string locally first

---

## Next Steps

- [ ] Add rate limiting middleware (slowapi)
- [ ] Implement password reset flow
- [ ] Add email verification workflow
- [ ] Set up session cleanup job
- [ ] Add comprehensive error handling
- [ ] Write integration tests
- [ ] Set up monitoring and logging

---

## References

- [Better Auth Documentation](https://www.better-auth.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Hugging Face Spaces Guide](https://huggingface.co/docs/hub/spaces)
- [Vercel Deployment Guide](https://vercel.com/docs)
- [Neon Postgres Guide](https://neon.tech/docs)
