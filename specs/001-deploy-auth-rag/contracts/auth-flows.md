# Authentication Flows: Deploy Authenticated RAG Backend and UI

**Feature**: [001-deploy-auth-rag](../spec.md)
**Date**: 2025-12-27

## Overview

This document describes the authentication flows between the Next.js frontend (deployed on Vercel) and FastAPI backend (deployed on Hugging Face Spaces) using Better Auth-compatible session cookies.

## Security Properties

- **Session Cookies**: httpOnly, secure, SameSite=Lax
- **Password Hashing**: bcrypt with work factor 12
- **Rate Limiting**: 10 requests/minute per user
- **Session Duration**: 7 days (configurable)
- **Token Format**: Opaque session tokens (not JWTs)

---

## Flow 1: User Registration

### Sequence

```
User (Frontend) → Backend API → Database
```

### Steps

1. **Frontend**: User enters email and password on sign-up page
2. **Frontend**: Validates email format and password strength (client-side)
3. **Frontend**: Sends POST request to `/api/auth/register`
   ```json
   {
     "email": "user@example.com",
     "password": "SecurePass123"
   }
   ```
4. **Backend**: Validates email format (server-side)
5. **Backend**: Checks if email already exists in database
   - If exists: Return 409 Conflict
   - If not exists: Continue
6. **Backend**: Hashes password using bcrypt (work factor 12)
7. **Backend**: Inserts new user record into database
   ```sql
   INSERT INTO users (email, password_hash)
   VALUES ('user@example.com', '$2b$12$...')
   ```
8. **Backend**: Returns 201 Created with user_id and email
9. **Frontend**: Redirects user to sign-in page

### Success Response (201)

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "message": "Account created successfully"
}
```

### Error Responses

- **400 Bad Request**: Invalid email format or password too short
  ```json
  {
    "detail": "Email format is invalid"
  }
  ```
- **409 Conflict**: Email already in use
  ```json
  {
    "detail": "Email already in use"
  }
  ```

### Edge Cases

- What if email format is invalid? → Backend validates and returns 400
- What if password is too weak? → Frontend enforces, backend validates minimum 8 characters
- What if database insert fails? → Backend returns 500 Internal Server Error

---

## Flow 2: User Sign-In

### Sequence

```
User (Frontend) → Backend API → Database → Backend API → Frontend (Cookie)
```

### Steps

1. **Frontend**: User enters email and password on sign-in page
2. **Frontend**: Validates email format (client-side)
3. **Frontend**: Sends POST request to `/api/auth/sign-in`
   ```json
   {
     "email": "user@example.com",
     "password": "SecurePass123"
   }
   ```
4. **Backend**: Validates email format (server-side)
5. **Backend**: Retrieves user record by email from database
   ```sql
   SELECT id, email, password_hash FROM users WHERE email = 'user@example.com'
   ```
6. **Backend**: Verifies password hash using bcrypt
   - If invalid: Return 401 Unauthorized
   - If valid: Continue
7. **Backend**: Generates cryptographically random session token
   ```python
   import secrets
   session_token = secrets.token_urlsafe(32)
   ```
8. **Backend**: Inserts session record into database
   ```sql
   INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
   VALUES ('...', '...', NOW() + INTERVAL '7 days', '192.168.1.1', 'Mozilla/5.0...')
   ```
9. **Backend**: Returns 200 OK with user information
10. **Backend**: Sets httpOnly, secure, SameSite=lax session cookie
    ```
    Set-Cookie: session_token=abc123...; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=604800
    ```
11. **Frontend**: Stores cookie automatically (httpOnly prevents JavaScript access)
12. **Frontend**: Redirects user to chat page

### Success Response (200)

**Headers**:
```
Set-Cookie: session_token=abc123...; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=604800
```

**Body**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "message": "Signed in successfully"
}
```

### Error Responses

- **401 Unauthorized**: Invalid email or password
  ```json
  {
    "detail": "Invalid email or password"
  }
  ```
- **429 Too Many Requests**: Rate limit exceeded (10 attempts per 5 minutes)
  ```json
  {
    "detail": "Too many sign-in attempts. Please try again later."
  }
  ```
  ```
  Retry-After: 300
  ```

### Edge Cases

- What if user account doesn't exist? → Backend returns 401 (invalid credentials - don't reveal user existence)
- What if session already exists? → Create new session (allow multiple concurrent sessions)
- What if database insert fails? → Backend returns 500 Internal Server Error
- What if rate limit exceeded? → Backend returns 429 with Retry-After header

---

## Flow 3: Protected Resource Access (Chat)

### Sequence

```
User (Frontend with Cookie) → Backend API (Middleware) → RAG Service → Backend API → Frontend
```

### Steps

1. **Frontend**: User sends chat message via protected page
2. **Frontend**: Browser automatically includes session cookie in request
   ```
   Cookie: session_token=abc123...
   ```
3. **Backend**: Auth middleware extracts session_token from cookie
4. **Backend**: Retrieves session record from database
   ```sql
   SELECT id, user_id, expires_at FROM sessions WHERE session_token = 'abc123...'
   ```
5. **Backend**: Validates session
   - If not found: Return 401 Unauthorized
   - If expired: Return 401 Unauthorized
   - If valid: Continue
6. **Backend**: Rate limiter checks per-user request count
   - If exceeded: Return 429 Too Many Requests
   - If within limit: Continue
7. **Backend**: Forwards request to RAG service with user context
8. **RAG Service**: Processes query and returns response
9. **Backend**: Returns 200 OK with RAG response
10. **Frontend**: Displays response in chat interface

### Request (POST /api/chat/message)

**Headers**:
```
Cookie: session_token=abc123...
```

**Body**:
```json
{
  "message": "What are the key principles of AI safety?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Success Response (200)

```json
{
  "user_message_id": "550e8400-e29b-41d4-a716-446655440001",
  "response": "The key principles of AI safety include transparency, fairness, accountability, and privacy...",
  "response_message_id": "550e8400-e29b-41d4-a716-446655440002",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-12-27T10:35:00Z"
}
```

### Error Responses

- **401 Unauthorized**: No valid session or expired
  ```json
  {
    "detail": "Authentication required"
  }
  ```
- **429 Too Many Requests**: Rate limit exceeded (10 requests per minute)
  ```json
  {
    "detail": "Rate limit exceeded. Please wait before sending another message."
  }
  ```
  ```
  Retry-After: 45
  ```
- **503 Service Unavailable**: Backend or RAG service unavailable
  ```json
  {
    "detail": "Service temporarily unavailable. Please try again later."
  }
  ```

### Edge Cases

- What if session cookie missing? → Middleware returns 401, frontend redirects to sign-in
- What if session expired? → Middleware returns 401, frontend redirects to sign-in
- What if rate limit exceeded? → Backend returns 429 with Retry-After, frontend shows countdown
- What if RAG service times out? → Backend returns 503, frontend shows error message
- What if multiple concurrent requests from same user? → Rate limiter tracks per-user count

---

## Flow 4: User Sign-Out

### Sequence

```
User (Frontend) → Backend API → Database → Frontend (Cookie Cleared)
```

### Steps

1. **Frontend**: User clicks sign-out button
2. **Frontend**: Sends POST request to `/api/auth/sign-out`
3. **Frontend**: Browser automatically includes session cookie
4. **Backend**: Extracts session_token from cookie
5. **Backend**: Deletes session record from database
   ```sql
   DELETE FROM sessions WHERE session_token = 'abc123...'
   ```
6. **Backend**: Returns 200 OK
7. **Backend**: Clears session cookie (Max-Age=0)
    ```
    Set-Cookie: session_token=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0
    ```
8. **Frontend**: Redirects user to sign-in page

### Success Response (200)

**Headers**:
```
Set-Cookie: session_token=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0
```

**Body**:
```json
{
  "message": "Signed out successfully"
}
```

### Error Responses

- **401 Unauthorized**: No valid session (user not signed in)
  ```json
  {
    "detail": "Not authenticated"
  }
  ```

### Edge Cases

- What if session already deleted? → Backend returns 401 (idempotent - safe to call multiple times)
- What if cookie missing? → Backend returns 401
- What if database delete fails? → Backend logs error but clears cookie anyway (failsafe)

---

## CORS Configuration

### Backend (FastAPI)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### Frontend (Next.js API Client)

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-space.hf.space/api';

async function apiRequest(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: 'include', // Required for cookies
    ...options,
  });
  return response;
}
```

---

## Session Cookie Properties

| Property | Value | Purpose |
|-----------|-------|---------|
| Name | `session_token` | Cookie identifier |
| Value | Opaque token (32+ bytes) | Session identifier (not JWT) |
| Path | `/` | Available to all paths |
| httpOnly | `True` | Prevents JavaScript access (XSS protection) |
| Secure | `True` | Transmits only over HTTPS |
| SameSite | `Lax` | Allows top-level navigation, blocks CSRF |
| Max-Age | `604800` seconds (7 days) | Session duration |

---

## Security Headers (Backend)

FastAPI middleware sets the following security headers:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking |
| `X-XSS-Protection` | `1; mode=block` | XSS filtering |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | HSTS enforcement |
| `Content-Security-Policy` | Restrictive policy | XSS protection |

---

## Logging Events

The following authentication events are logged (no chat content):

| Event | Logged Data |
|-------|-------------|
| Sign-in success | user_id, email, timestamp, ip_address |
| Sign-in failure | email, reason (invalid credentials), timestamp, ip_address |
| Sign-out | user_id, timestamp |
| Session expiration | user_id, session_id, timestamp |
| Rate limit exceeded | user_id, timestamp, endpoint |
| System error | error_type, error_message, stack_trace, timestamp |

### Example Log Entry

```json
{
  "event": "sign_in_success",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "timestamp": "2025-12-27T10:30:00Z",
  "ip_address": "192.168.1.1"
}
```

---

## Frontend Integration (Better Auth Next.js SDK)

### Configuration

```typescript
// lib/auth.ts
import { createAuthClient } from 'better-auth/react'

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://your-space.hf.space',
  credentials: 'include',
})
```

### Sign-In Form

```typescript
// components/auth/SignInForm.tsx
import { authClient } from '@/lib/auth'

export default function SignInForm() {
  async function signIn(formData: FormData) {
    const result = await authClient.signIn.email({
      email: formData.get('email') as string,
      password: formData.get('password') as string,
    })

    if (result.error) {
      console.error('Sign in failed:', result.error)
      return
    }

    // Redirect to chat page
    window.location.href = '/chat'
  }

  return (
    <form action={signIn}>
      <input name="email" type="email" required />
      <input name="password" type="password" required />
      <button type="submit">Sign In</button>
    </form>
  )
}
```

### Protected Route (Chat Page)

```typescript
// app/chat/page.tsx
import { authClient } from '@/lib/auth'

export default async function ChatPage() {
  const session = await authClient.getSession()

  if (!session) {
    redirect('/sign-in')
  }

  return <ChatInterface user={session.user} />
}
```

---

## Troubleshooting

### Issue: Session cookie not being sent

**Symptoms**: Frontend receives 401 Unauthorized even after sign-in

**Causes**:
- CORS `allow_credentials` not set to `True` on backend
- Frontend `credentials: 'include'` not set in fetch
- Cookie domain mismatch (must be same as request origin)
- Cookie `secure` flag set but frontend accessed via HTTP

**Solution**:
1. Verify CORS configuration on backend
2. Verify `credentials: 'include'` in frontend API client
3. Ensure both frontend and backend use HTTPS
4. Check browser DevTools Application > Cookies

### Issue: Session expires too quickly

**Symptoms**: Users are signed out frequently

**Causes**:
- Session duration too short (7 days is configured value)
- Browser clearing cookies automatically
- Server time clock skew

**Solution**:
1. Increase session duration in backend configuration
2. Check browser settings for automatic cookie clearing
3. Sync server time with NTP

### Issue: CORS errors in browser console

**Symptoms**: CORS policy blocked request in browser DevTools

**Causes**:
- Frontend origin not in `allow_origins` list
- Preflight OPTIONS request failing
- Missing CORS headers on backend

**Solution**:
1. Add frontend URL to `allow_origins`
2. Verify OPTIONS method allowed in CORS config
3. Check network tab for OPTIONS request status

### Issue: Rate limit blocking legitimate users

**Symptoms**: Users getting 429 errors during normal use

**Causes**:
- Rate limit too strict (10 req/min)
- Concurrent requests from multiple tabs
- User spamming messages

**Solution**:
1. Monitor rate limit logs for patterns
2. Adjust rate limit if too restrictive
3. Implement sliding window rate limiting for burst handling

---

## References

- Better Auth Documentation: https://www.better-auth.com/docs
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
- Session Cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
- bcrypt: https://pypi.org/project/bcrypt/
