# Deployment Instructions: Phase 4 - Auth Backend

**Feature**: 001-deploy-auth-rag
**Date**: 2025-12-27
**Purpose**: Step-by-step guide to deploy backend to Hugging Face and connect to frontend

---

## Prerequisites

- [x] Hugging Face account (free tier) - https://huggingface.co/join
- [x] Neon Postgres database already configured
- [x] Git configured locally
- [x] Python 3.11+ installed

---

## Deployment Steps

### Step 1: Deploy Backend to Hugging Face

#### 1.1 Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Configure:
   - **Space name**: `rag-auth-backend` (or your preferred name)
   - **License**: MIT
   - **Space SDK**: Docker
   - **Visibility**: Public (or Private)
3. Click "Create Space"

#### 1.2 Clone Space Locally

```bash
# Replace YOUR_USERNAME with your Hugging Face username
git clone https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend
cd rag-auth-backend
```

#### 1.3 Copy Backend Files

```bash
# From your main project directory (book_hackathon_main)
cp -r backend/src/* rag-auth-backend/src/
cp backend/requirements.txt rag-auth-backend/
cp backend/Dockerfile rag-auth-backend/
cp backend/.env.example rag-auth-backend/

# Create .env with your actual values
cat > rag-auth-backend/.env << 'EOF'
# Neon PostgreSQL Database
DATABASE_URL=postgresql://neondb_owner:npg_Ly9UORKo8ert@ep-plain-violet-adu773n5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Secret Key for Session Tokens
SECRET_KEY=u7xN9ZqP3mK8fR2cA5sW4vL1yT6hJ9eM7nB3dC8p

# Frontend URL (Vercel)
FRONTEND_URL=https://book-hackathon-blond.vercel.app
EOF
```

#### 1.4 Commit and Push

```bash
git add .
git commit -m "Deploy authenticated RAG backend with auth endpoints"
git push
```

#### 1.5 Monitor Build

1. Go to https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend
2. Click on "Files" tab to monitor build logs
3. Monitor build logs (should take 5-10 minutes)
4. Look for successful startup message in logs:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

#### 1.6 Set Environment Variables in Hugging Face (Optional but Recommended)

Instead of including `.env` in the repository, you can set environment variables in Hugging Face Space Settings:

1. Go to your Space on Hugging Face
2. Click "Settings" tab
3. Scroll to "Variables & secrets"
4. Click "New variable" and add:

```
DATABASE_URL=postgresql://neondb_owner:npg_Ly9UORKo8ert@ep-plain-violet-adu773n5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
SECRET_KEY=u7xN9ZqP3mK8fR2cA5sW4vL1yT6hJ9eM7nB3dC8p
FRONTEND_URL=https://book-hackathon-blond.vercel.app
```

5. Make sure they're marked as "Secret" (not visible publicly)

### Step 2: Test Backend Deployment

#### 2.1 Test Health Endpoint

```bash
# Replace YOUR_USERNAME with your Hugging Face username
curl https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T12:00:00Z"
}
```

#### 2.2 Test Registration Endpoint

```bash
curl -X POST https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

**Expected Response** (201):
```json
{
  "user_id": "...",
  "email": "test@example.com",
  "message": "Account created successfully"
}
```

**Expected Response** (409 - duplicate email):
```json
{
  "detail": "Email already in use"
}
```

#### 2.3 Test Sign-In Endpoint

```bash
curl -X POST https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

**Expected Response** (200):
```json
{
  "user_id": "...",
  "email": "test@example.com",
  "message": "Signed in successfully"
}
```

**Expected Response** (401 - invalid credentials):
```json
{
  "detail": "Invalid email or password"
}
```

#### 2.4 Test Unauthenticated Request to Protected Route

```bash
curl https://huggingface.co/spaces/YOUR_USERNAME/rag-auth-backend/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

**Expected Response** (401):
```json
{
  "detail": "Authentication required"
}
```

### Step 3: Update Frontend Configuration

1. **Edit frontend/.env.local**:

```bash
cd frontend
```

Update the file:
```bash
# Backend API URL
# Update this to your deployed Hugging Face Space URL
API_URL=https://YOUR_USERNAME.hf.space/api

# For local development:
# API_URL=http://localhost:7860/api
```

2. **Deploy Frontend to Vercel**:

```bash
cd frontend
npm run build
vercel --prod
```

Or simply push changes to GitHub - Vercel will auto-deploy.

### Step 4: Test Production Integration

1. **Test Registration Flow**:
   - Visit `https://book-hackathon-blond.vercel.app/sign-up`
   - Enter email and password
   - Verify creation success and redirect to `/sign-in`

2. **Test Sign-In Flow**:
   - Visit `https://book-hackathon-blond.vercel.app/sign-in`
   - Enter credentials
   - Verify redirect to `/chat`
   - Open DevTools → Application → Cookies
   - Confirm `session_token` cookie exists with `httpOnly` flag

3. **Verify Session Persistence**:
   - Refresh the `/chat` page
   - Verify you're still on `/chat` (not redirected to `/sign-in`)
   - Check session cookie still exists in Application → Cookies

4. **Test Sign-Out Flow**:
   - Click Sign Out button in `/chat`
   - Verify redirect to `/sign-in`
   - Confirm session cookie is cleared (expires in past)

5. **Test Protected Routes**:
   - Try accessing `/chat` without sign-in
   - Verify redirect to `/sign-in`
   - Check DevTools Network tab for `401 Unauthorized` responses

---

## Troubleshooting

### Issue: Hugging Face Build Fails

**Symptoms**: Docker image build fails with errors

**Solutions**:
- Check `requirements.txt` has valid package versions
- Verify `Dockerfile` uses correct Python base image (3.11-slim)
- Check build logs in Hugging Face Files tab for specific errors
- Ensure all Python imports are correct in source files
- Verify all files are UTF-8 encoded

### Issue: 401 Unauthorized on All Requests

**Symptoms**: Even `/health` endpoint returns 401

**Solutions**:
- Verify `DATABASE_URL` is set correctly in Hugging Face
- Check database is accessible (Neon database not paused)
- Verify `init_db()` is being called on startup (check logs)
- Check application logs for database connection errors
- Ensure SSL mode is enabled in connection string (`sslmode=require`)

### Issue: CORS Errors in Browser

**Symptoms**: Browser DevTools Console shows CORS errors like:
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**Solutions**:
- Verify `FRONTEND_URL` matches Vercel URL exactly (no trailing slashes)
- Check CORS middleware in `backend/src/main.py` has `allow_credentials=True`
- Ensure `allow_origins` includes your Vercel URL
- Re-deploy backend after CORS configuration changes
- Wait 5-10 minutes for Hugging Face to rebuild and apply changes
- Check that both domains use HTTPS

### Issue: Session Cookie Not Set

**Symptoms**: Sign-in request succeeds but no cookie appears in browser

**Solutions**:
- Check response headers include `Set-Cookie` header
- Verify cookie has correct attributes: `httpOnly`, `secure`, `SameSite=lax`
- Ensure both frontend and backend use HTTPS
- Check for domain/hostname mismatch between frontend and backend
- Verify `expires_at` is in the future (7 days from now)
- Check browser DevTools for cookie details

### Issue: Rate Limit Errors Too Quickly

**Symptoms**: Getting 429 errors after 1-2 requests

**Solutions**:
- Rate limit is 10 requests per hour (registration) or 10 per 5 minutes (sign-in)
- Wait for rate limit to reset before trying again
- Check rate limiting key function is working correctly (`slowapi.util.get_remote_address`)
- Verify Redis/state backend is not causing issues
- Check different IP addresses (might be shared in development environment)

---

## Local Testing

### Backend Local Testing

1. **Start Backend**:
```bash
cd backend
python -m uvicorn src.main:app --reload --port 7860
```

2. **Run Tests**:
```bash
cd backend
pytest src/tests/unit/ -v
pytest src/tests/contract/ -v
pytest src/tests/integration/ -v
```

3. **Test Endpoints**:
```bash
# Health check
curl http://localhost:7860/health

# Registration
curl -X POST http://localhost:7860/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

### Frontend Local Testing

1. **Start Frontend**:
```bash
cd frontend
npm start
```

2. **Test Flow**:
   - Open http://localhost:3000/sign-up
   - Create account
   - Sign in
   - Verify session cookie
   - Access protected /chat page

---

## Pre-Deployment Checklist

### Backend
- [ ] All tests pass locally
- [ ] `DATABASE_URL` is correct (Neon connection)
- [ ] `SECRET_KEY` is set and secure
- [ ] `FRONTEND_URL` points to Vercel deployment
- [ ] Dockerfile is ready (Python 3.11-slim, port 7860)
- [ ] requirements.txt has all dependencies
- [ ] Health endpoint is accessible
- [ ] Auth endpoints are accessible
- [ ] CORS is configured correctly

### Frontend
- [ ] API_URL is set in .env.local
- [ ] AuthProvider wraps entire app
- [ ] Sign-in page is created
- [ ] Sign-up page is created
- [ ] Chat page is created
- [ ] Forms have error handling
- [ ] Forms have loading states

### Environment Variables
- [ ] Backend .env has DATABASE_URL
- [ ] Backend .env has SECRET_KEY
- [ ] Backend .env has FRONTEND_URL
- [ ] Frontend .env.local has API_URL
- [ ] All secrets are NOT committed to git

---

## Post-Deployment Checklist

### Backend Deployment
- [ ] Hugging Face space is built (check status in Files tab)
- [ ] Health check returns 200: `curl https://.../health`
- [ ] Register endpoint returns 201: `curl -X POST .../api/auth/register`
- [ ] Sign-in endpoint returns 200: `curl -X POST .../api/auth/sign-in`
- [ ] Sign-out endpoint returns 200: `curl -X POST .../api/auth/sign-out`
- [ ] Unauthenticated requests return 401
- [ ] Rate limiting works (429 after exceeding limit)
- [ ] No errors in Hugging Face logs

### Frontend Integration
- [ ] Frontend deployed to Vercel
- [ ] API_URL points to Hugging Face space
- [ ] Registration flow works end-to-end
- [ ] Sign-in flow works end-to-end
- [ ] Session cookie is set (check DevTools)
- [ ] Protected routes redirect unauthenticated users
- [ ] Sign-out clears session cookie
- [ ] Session persists across page reloads
- [ ] No CORS errors in browser console

---

## Next Steps

### Phase 5: User Story 3 - Authenticated Chat Interface (Optional)

**Goal**: Authenticated users can access protected chat interface, send messages to RAG system, and receive responses

**Tasks** (from tasks.md Phase 5):
- T051-T054: Tests for chat endpoint and page protection
- T055-T069: Implement chat endpoint with RAG integration
- T070-T078: Polish and cross-cutting improvements

---

## Documentation

- [Phase 4 Complete Guide](PHASE4-COMPLETE.md)
- [User Story 2 Complete](USER-STORY-2-COMPLETE.md)
- [Hugging Face Deployment](HUGGINGFACE-DEPLOYMENT.md)
- [Frontend Integration](FRONTEND-INTEGRATION.md)
- [Backend API Contract](contracts/backend-api.yaml)
- [Tasks List](tasks.md)

---

## Status

✅ **Code Complete**: All Phase 4 tasks (T028-T050) implemented
✅ **Tests Complete**: All unit, contract, and integration tests written
✅ **Frontend Complete**: All authentication pages and components created
⏳ **Deployment Pending**: Manual steps to deploy backend to Hugging Face
⏳ **Integration Pending**: Manual steps to connect frontend to deployed backend

**Estimated Time to Complete Deployment**: 30-45 minutes
