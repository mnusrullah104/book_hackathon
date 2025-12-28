# Hugging Face Spaces Deployment Guide

**Feature**: 001-deploy-auth-rag (MVP)
**Date**: 2025-12-27
**Purpose**: Deploy FastAPI backend with authentication middleware to Hugging Face Spaces

---

## Prerequisites

1. **Hugging Face Account**: Sign up at https://huggingface.co (free tier)
2. **Neon Postgres Database**: Sign up at https://neon.tech (free tier)
3. **Git Configured**: Git should be configured locally
4. **Python 3.11+**: Installed for local testing

---

## Step 1: Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Configure:
   - **Space name**: `rag-auth-backend`
   - **License**: MIT
   - **Space SDK**: Docker
   - **Visibility**: Public (or Private for MVP)

---

## Step 2: Clone Space Locally

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend
cd rag-auth-backend
```

---

## Step 3: Copy Backend Files

Copy all backend source code to the space repository:

```bash
# From your main project directory
cp -r backend/src/* rag-auth-backend/src/
cp backend/requirements.txt rag-auth-backend/
cp backend/Dockerfile rag-auth-backend/
cp backend/.env.example rag-auth-backend/
```

**Important Files**:
- `src/main.py` - Main FastAPI app with middleware
- `src/models/database.py` - Database connection and Base
- `src/models/user.py` - User model
- `src/models/session.py` - Session model
- `src/services/auth.py` - Authentication services
- `src/api/routes/health.py` - Health check endpoint
- `src/api/middleware/auth.py` - Authentication middleware
- `src/api/middleware/security.py` - Security headers middleware
- `src/api/middleware/rate_limit.py` - Rate limiting middleware
- `src/api/middleware/logging.py` - Structured logging middleware
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration

---

## Step 4: Configure Environment Variables in Hugging Face

In the Hugging Face Space Settings → Variables & secrets (README):

```bash
# Neon Postgres Connection
DATABASE_URL=postgresql://USER:PASSWORD@ep-XYZ.aws.neon.tech/neondb?sslmode=require

# Secret Key for Session Tokens
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key-here

# Frontend URL for CORS
# Update with your actual Vercel deployment URL
FRONTEND_URL=https://your-app.vercel.app
```

### Getting Database URL from Neon

1. Go to https://console.neon.tech
2. Select your project
3. Go to "Connection Details"
4. Copy the "Connection string" (psql format)
5. Replace `user:password@...` with your actual credentials

---

## Step 5: Verify Dockerfile

The `Dockerfile` should contain:

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

---

## Step 6: Commit and Push

```bash
git add .
git commit -m "Deploy authenticated RAG backend with auth middleware"
git push
```

---

## Step 7: Monitor Deployment

1. Go to https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend
2. Click on "Files" tab to monitor build logs
3. Wait 5-10 minutes for Docker image to build and start
4. Check the "Logs" tab for application logs
5. Look for successful startup message in logs

**Expected Logs**:
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

---

## Step 8: Test Deployment

### Test 1: Health Check (Public)

```bash
curl https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T12:00:00Z"
}
```

### Test 2: Unauthenticated Request (Protected - Should Return 401)

```bash
curl https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

**Expected Response**: `401 Unauthorized`

### Test 3: Authentication Middleware (Should Return 401 - No Session Yet)

```bash
curl https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=invalid_token" \
  -d '{"message":"test"}'
```

**Expected Response**: `401 Unauthorized`

---

## Step 9: Set Up Neon Database Schema

The FastAPI app will automatically create tables on startup. To verify:

1. Go to https://console.neon.tech
2. Select your project
3. Go to "SQL Editor"
4. Verify tables exist:
   - `users` table with columns: id, email, password_hash, created_at, updated_at
   - `sessions` table with columns: id, user_id, session_token, expires_at, created_at, ip_address, user_agent

**Manual Schema Creation (if needed)**:

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

---

## Troubleshooting

### Issue: Build Fails

**Symptoms**: Docker image build fails with errors
**Solutions**:
- Check `requirements.txt` has no invalid package versions
- Verify Dockerfile uses correct Python base image
- Check Hugging Face build logs for specific error messages

### Issue: 401 Unauthorized for All Requests

**Symptoms**: Even `/health` endpoint returns 401
**Solutions**:
- Verify `DATABASE_URL` environment variable is set correctly
- Check database is accessible (Neon database not paused)
- Verify init_db() is being called on startup
- Check application logs for database connection errors

### Issue: 500 Internal Server Error

**Symptoms**: Health check or other endpoints return 500
**Solutions**:
- Check application logs for stack trace
- Verify all Python imports are correct
- Check environment variables are set
- Check database schema is correct

### Issue: CORS Errors

**Symptoms**: Browser console shows CORS errors when accessing from Vercel
**Solutions**:
- Verify `FRONTEND_URL` matches your Vercel deployment URL exactly
- Check `allow_credentials=True` is set in CORS configuration
- Check `allow_origins` includes your Vercel URL

### Issue: Space Not Responding

**Symptoms**: Space shows "Sleeping" status
**Solutions**:
- Hugging Face Spaces sleep after inactivity
- Make a request to wake it up (try health endpoint)
- Verify Space is configured with sufficient resources

---

## Next Steps

After successful backend deployment:

1. **Frontend Integration** (User Story 2):
   - Configure Better Auth in Next.js
   - Create sign-in/sign-up pages
   - Connect to backend `/api/auth/register`, `/api/auth/sign-in`, `/api/auth/sign-out`

2. **Protected Chat Interface** (User Story 3):
   - Create protected chat page
   - Implement message sending to `/api/chat/message`
   - Add session management

---

## Environment Variables Reference

| Variable | Description | Example |
|-----------|-------------|---------|
| DATABASE_URL | Neon Postgres connection string | `postgresql://user:pass@ep-xyz.aws.neon.tech/neondb` |
| SECRET_KEY | Secret key for session tokens | Random 32-char string |
| FRONTEND_URL | Vercel frontend URL (CORS) | `https://your-app.vercel.app` |

---

## References

- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Neon Postgres Documentation](https://neon.tech/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Better Auth Documentation](https://www.better-auth.com/)
