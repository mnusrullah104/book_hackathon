# Frontend Integration Guide: Better Auth & Vercel

**Feature**: 001-deploy-auth-rag
**Date**: 2025-12-27
**Purpose**: Connect Next.js frontend with deployed backend using Better Auth

---

## Overview

This guide covers integrating the Next.js frontend (already deployed on Vercel) with the FastAPI backend deployed on Hugging Face Spaces using Better Auth for authentication.

### Authentication Flow

```
User (Frontend) → Better Auth (Next.js SDK) → Session Cookie → Backend FastAPI
                                                        ↓
                                                    Token Verification → Protected Endpoint
```

---

## Step 1: Install Better Auth Dependencies

```bash
cd frontend
npm install better-auth @auth/core
```

### Alternative: Yarn

```bash
yarn add better-auth @auth/core
```

---

## Step 2: Create Auth Client Configuration

Create `frontend/src/lib/auth.ts`:

```typescript
import { createAuthClient } from 'better-auth/react'

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'https://your-space.hf.space/api',
  credentials: 'include',
})

export type Session = Awaited<ReturnType<typeof authClient.getSession>>
```

**Key Points**:
- `baseURL`: Points to backend `/api` path
- `credentials: 'include'`: Critical - ensures cookies are sent with requests
- Environment variable `NEXT_PUBLIC_API_URL`: Can be different per environment (development vs production)

---

## Step 3: Create Sign-In Page

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
      <div className="max-w-md w-full space-y-8 p-8 bg-gray-50 rounded-lg shadow">
        <h1 className="text-3xl font-bold text-center text-gray-900">Sign In</h1>

        <form action={signIn} className="space-y-4">
          {/* Email Input */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="you@example.com"
            />
          </div>

          {/* Password Input */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              minLength={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••••"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Link to Sign Up */}
        <p className="text-center text-sm text-gray-600">
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

---

## Step 4: Create Sign-Up Page

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
      <div className="max-w-md w-full space-y-8 p-8 bg-gray-50 rounded-lg shadow">
        <h1 className="text-3xl font-bold text-center text-gray-900">Create Account</h1>

        <form action={signUp} className="space-y-4">
          {/* Email Input */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="you@example.com"
            />
          </div>

          {/* Password Input */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password (min 8 characters)
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              minLength={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••••"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        {/* Link to Sign In */}
        <p className="text-center text-sm text-gray-600">
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

---

## Step 5: Create Protected Chat Page

Create `frontend/src/app/chat/page.tsx`:

```typescript
import { authClient } from '@/lib/auth'

export default async function ChatPage() {
  const session = await authClient.getSession()

  if (!session) {
    redirect('/sign-in')
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Chat</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{session.user.email}</span>
            <button
              onClick={async () => {
                await authClient.signOut()
                window.location.href = '/sign-in'
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Sign Out
            </button>
          </div>
        </header>

        {/* Chat Interface Placeholder */}
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-center">
            Chat interface implementation placeholder.
            <br />
            This page is protected and only accessible to authenticated users.
          </p>
        </div>
      </div>
    </div>
  )
}
```

**Key Points**:
- Server component (`export default async function`) - runs on server, can safely call `await authClient.getSession()`
- Session verification happens server-side before page renders
- Redirect to `/sign-in` if no valid session
- User email accessible from `session.user.email`

---

## Step 6: Create Chat Interface Component

Create `frontend/src/components/chat/ChatInterface.tsx`:

```typescript
'use client'

import { useState } from 'react'
import { authClient } from '@/lib/auth'

interface Message {
  id: string
  sender: 'user' | 'system'
  content: string
  timestamp: string
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>()

  async function sendMessage(e: React.FormEvent) {
    e.preventDefault()
    setError(undefined)

    if (!input.trim()) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      sender: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Cookie is automatically included by browser (httpOnly prevents JS access)
        },
        credentials: 'include', // Critical: ensures session cookie is sent
        body: JSON.stringify({ message: userMessage.content }),
      })

      const data = await response.json()

      const systemMessage: Message = {
        id: data.response_message_id || crypto.randomUUID(),
        sender: 'system',
        content: data.response,
        timestamp: data.timestamp || new Date().toISOString(),
      }

      setMessages(prev => [...prev, systemMessage])
    } catch (err: any) {
      if (err instanceof Error) {
        if (err.message.includes('401') || err.status === 401) {
          setError('Session expired. Please sign in again.')
          setTimeout(() => {
            window.location.href = '/sign-in'
          }, 2000)
        } else if (err.message.includes('429') || err.status === 429) {
          setError('Rate limit exceeded. Please wait before sending another message.')
        } else {
          setError('Failed to send message. Please try again.')
        }
      } else {
        setError('An error occurred. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center">
      <div className="max-w-4xl w-full bg-white rounded-lg shadow p-8">
        {/* Header */}
        <h2 className="text-2xl font-bold text-gray-900 mb-6">RAG Chat</h2>
        <p className="text-gray-600 mb-2">Authenticated chat interface</p>

        {/* Chat Messages */}
        <div className="h-96 overflow-y-auto mb-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500">
              Send a message to start chatting with the RAG system.
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={msg.id}
                className={`p-4 rounded-lg ${
                  msg.sender === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <div className="text-sm font-semibold mb-1">
                  {msg.sender === 'user' ? 'You' : 'System'}
                </div>
                <div className="text-gray-800">{msg.content}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={sendMessage} className="border-t border-gray-200 rounded-lg p-4">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your message here..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={4}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

**Key Points**:
- `credentials: 'include'` - Automatically includes session cookie in requests
- Error handling for 401 (session expired) - redirects to sign-in
- Error handling for 429 (rate limit) - shows error message
- In-memory messages (no persistence as per spec Out of Scope)

---

## Step 7: Configure Environment Variables

### For Local Development

Create `frontend/.env.local` (this file should NOT be committed to git):

```bash
NEXT_PUBLIC_API_URL=http://localhost:7860/api
```

### For Production (Vercel)

Set environment variable in Vercel Dashboard:
- Go to Project Settings → Environment Variables
- Add: `NEXT_PUBLIC_API_URL=https://your-space.hf.space/api`

**Important**: `.env.local` is in `.gitignore` (it should be by default in Next.js)

---

## Step 8: Update GitIgnore (if needed)

Verify `.gitignore` contains:

```
# Environment variables
.env
.env*.local
.env.production

# Dependencies
node_modules/

# Build outputs
.next
dist
build

# Logs
*.log

# Cache
.cache
```

If not, update `frontend/.gitignore`:

```bash
# Environment variables
.env
.env*.local
.env.production

# Dependencies
node_modules/

# Build outputs
.next
dist
build

# Logs
*.log

# Cache
.cache
```

---

## Step 9: Test Integration Locally

### Prerequisites

1. Backend running locally:
   ```bash
   cd backend
   python -m uvicorn src.main:app --reload --port 7860
   ```

2. Frontend running locally:
   ```bash
   cd frontend
   npm run dev
   ```

### Test Flow

1. **Navigate to** `http://localhost:3000/sign-up`
2. **Create account** with email and password
3. **Sign in** with those credentials
4. **Verify redirect** to `http://localhost:3000/chat`
5. **Send a message** and verify response

**Expected Behavior**:
- After sign-in, session cookie is set
- `/chat` page is accessible (not redirected to sign-in)
- Message is sent with session cookie
- Response is received and displayed
- Browser DevTools → Application → Cookies should show `session_token` cookie with httpOnly flag

---

## Step 10: Deploy Frontend to Vercel

If not already deployed, or to update with new authentication pages:

### Option A: Vercel CLI

```bash
npm install -g vercel
cd frontend
vercel
```

### Option B: Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Environment Variables: `NEXT_PUBLIC_API_URL=https://your-space.hf.space/api`
4. Click Deploy

---

## Step 11: Verify Production Deployment

### 1. Test Sign-In Flow

1. Open your Vercel deployment URL
2. Navigate to `/sign-in`
3. Sign in with test credentials
4. Verify redirect to `/chat`

### 2. Test Chat Functionality

1. On `/chat` page, send a message
2. Verify response is received from Hugging Face backend
3. Check browser DevTools → Network tab:
   - Request URL: `https://your-space.hf.space/api/chat/message`
   - Request Headers: Should include `Cookie: session_token=...`
   - Request Method: POST
   - Response Status: 200 (unless rate limited or error)

### 3. Test Session Persistence

1. Refresh the page
2. Verify you're still on `/chat` (not redirected to `/sign-in`)
3. Check session cookie still exists in Application → Cookies

### 4. Test Sign-Out

1. Click Sign Out button
2. Verify redirect to `/sign-in`
3. Try to navigate to `/chat` - should be redirected back to `/sign-in`

---

## Troubleshooting

### Issue: "Authentication required" even after sign-in

**Check**:
1. Is `NEXT_PUBLIC_API_URL` pointing to correct backend?
2. Is backend running and accessible?
3. Are cookies being sent? (DevTools → Network tab)
4. Is `credentials: 'include'` set in fetch calls?

**Solution**:
- Verify `NEXT_PUBLIC_API_URL` matches backend URL exactly
- Check backend health endpoint: `https://your-space.hf.space/health`
- Check that session cookie has `httpOnly` flag (browser DevTools)
- Ensure Better Auth is configured with correct `baseURL`

### Issue: "Session expired" errors

**Check**:
1. Backend session expiration time (should be 7 days)
2. System clock sync between client and server

**Solution**:
- Session may have expired during development
- Sign in again to get new session
- Check if backend has `init_db()` creating sessions on startup

### Issue: CORS errors in browser console

**Symptoms**: Browser DevTools shows CORS errors
```
Access to fetch at 'https://your-space.hf.space/api/...' from origin 'https://your-app.vercel.app' has been blocked by CORS policy
```

**Solution**:
1. Verify `FRONTEND_URL` in backend `.env` matches your Vercel URL exactly
2. Check CORS middleware in `backend/src/main.py`:
   - `allow_origins=[settings.FRONTEND_URL]` - must be exact match
   - `allow_credentials=True` - required for cookies
   - `allow_methods=["GET", "POST", "OPTIONS"]`
3. Re-deploy backend after CORS changes
4. Wait 5-10 minutes for Hugging Face to rebuild

### Issue: Rate limit exceeded too quickly

**Symptoms**: Getting 429 errors after 1-2 messages

**Check**:
- Rate limit is 10 requests per minute per user
- Counter resets after 60 seconds

**Solution**:
- Wait and retry
- If hitting rate limit consistently, adjust limit in `backend/src/api/middleware/rate_limit.py`
- Verify rate limiting is per-user, not global

### Issue: Frontend not receiving cookies

**Check**:
- Backend is setting cookie correctly?
- Cookie attributes: httpOnly, secure, SameSite?
- Domain matches? (Vercel subdomain vs backend subdomain)

**Solution**:
- Verify backend sets cookie with correct attributes
- Check Hugging Face Space logs for cookie setting errors
- SameSite=lax should work for cross-domain cookies

---

## Architecture Overview

### Component Relationships

```
┌─────────────────┐     ┌───────────────┐     ┌──────────────┐
│  Better Auth SDK   │────▶▶│  Session Cookie  │────▶▶│  Auth Middleware│─────▶▶
│  (Next.js)       │     │     │ (httpOnly)    │     │  (FastAPI)      │     │
│                 │     │     │              │     │                │     │
│  SignIn Component│     │     │              │     │  Protected     │─────▶▶
│                 │     │     │              │     │  Endpoint     │     │
└─────────────────┘     └───────────────┘     └──────────────┘     └────────────────┘

        │                      │             │
        │                      │             │
        ▼                      ▼             ▼
        └────────────────────────┘             │
                                             │
                                             ▼
                                       ┌───────────────┐
                                       │  RAG Service  │
                                       └───────────────┘
```

### Data Flow

1. **Sign-In**:
   - User enters credentials in SignInForm
   - `authClient.signIn.email()` sends POST to `/api/auth/sign-in`
   - Browser includes any existing cookies automatically
   - Backend verifies credentials, creates session, sets `session_token` cookie
   - Cookie stored with httpOnly flag (inaccessible to JavaScript)
   - Frontend receives response, redirects to `/chat`

2. **Send Message**:
   - User types message in ChatInterface
   - `fetch()` called with `credentials: 'include'`
   - Browser automatically includes `session_token` cookie (httpOnly, so JS can't see it)
   - Backend middleware extracts token from cookie, verifies session
   - If valid, processes request to RAG service
   - Response returned and displayed

---

## Security Considerations

### Session Cookies are Secure

- **httpOnly**: JavaScript cannot access cookies (prevents XSS from stealing tokens)
- **Secure**: Only transmitted over HTTPS (prevents MITM attacks)
- **SameSite=Lax**: Allows cross-site navigation, blocks most CSRF attacks

### Rate Limiting

- Per-user rate limiting (10 req/min)
- Enforced at middleware layer before endpoint processing
- Protects against abuse and resource exhaustion

### No Chat Content Logged

- Per spec requirements, chat messages are NOT logged
- Only authentication events are logged (sign-in, sign-out, failed attempts)
- This preserves user privacy

---

## Next Steps

1. **Test locally** with backend running on `localhost:7860`
2. **Deploy backend** to Hugging Face Spaces
3. **Update frontend** environment variable to point to deployed backend
4. **Deploy frontend** to Vercel (or update existing deployment)
5. **Test end-to-end** with deployed backend

---

## References

- [Better Auth Documentation](https://www.better-auth.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
