# Data Model: Deploy Authenticated RAG Backend and UI

**Feature**: [001-deploy-auth-rag](./spec.md)
**Date**: 2025-12-27
**Database**: Neon Serverless Postgres (free tier)

## Entity: User

**Purpose**: Represents an individual who can authenticate and access the chat system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the user |
| email | VARCHAR(255) | UNIQUE, NOT NULL, email format | User's email address for authentication |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password using bcrypt (work factor 12) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Validation Rules**:
- Email must be unique (no duplicate accounts)
- Email must be valid format (RFC 5322)
- Password minimum length: 8 characters
- Password must include at least one uppercase letter and one number (enforced by frontend)

**Relationships**:
- One-to-Many with Sessions (user_id → Session.user_id)

---

## Entity: Session

**Purpose**: Represents an active authenticated user interaction.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique session identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → User.id | Associated user |
| session_token | VARCHAR(255) | UNIQUE, NOT NULL | Session identifier (opaque token) |
| expires_at | TIMESTAMP | NOT NULL | Session expiration timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Session creation timestamp |
| ip_address | VARCHAR(45) | NULL | Client IP address for security audit |
| user_agent | TEXT | NULL | Client user agent string for audit |

**Validation Rules**:
- Session tokens must be cryptographically random (secrets.token_urlsafe)
- Session expiration: 7 days from creation (balance security and UX)
- Expired sessions automatically cleaned up

**Relationships**:
- Many-to-One with User (user_id → User.id)

**Indexes**:
- INDEX on user_id (for user session queries)
- INDEX on expires_at (for expired session cleanup)

---

## Entity: Message (In-Memory Only)

**Purpose**: Represents a single chat interaction (ephemeral - NOT persisted to database).

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique message identifier |
| conversation_id | UUID | Session-local conversation identifier |
| sender | ENUM | 'user' or 'system' |
| content | TEXT | Message content (user question or RAG response) |
| timestamp | TIMESTAMP | Message creation timestamp |
| status | ENUM | 'sent', 'received', 'failed' |

**Note**: Messages are ephemeral and stored in-memory only during active chat session. They are NOT persisted to database (per spec Out of Scope and privacy requirement).

---

## Entity: Conversation (In-Memory Only)

**Purpose**: Represents a sequence of related messages between a user and the RAG system.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique conversation identifier (session-local) |
| user_id | UUID | Associated user (from session) |
| created_at | TIMESTAMP | Conversation creation timestamp |
| updated_at | TIMESTAMP | Last message timestamp |
| messages | Array | Ordered list of Message objects |

**Note**: Conversations are ephemeral and stored in-memory only during active session. They are NOT persisted to database.

---

## Database Schema (DDL)

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

-- Unique constraint on email
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to auto-update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## State Transitions

### User Lifecycle

```
[New] → [Active] → [Inactive/Deleted]
```

- **New**: User account created via registration
- **Active**: User can sign in and access chat
- **Inactive/Deleted**: Not in scope for MVP (no account deletion feature)

### Session Lifecycle

```
[Created] → [Valid] → [Expired/Terminated]
```

- **Created**: Session created on successful sign-in
- **Valid**: Session is active, user can access protected resources
- **Expired/Terminated**: Session expires after 7 days OR user signs out

### Message Lifecycle

```
[Created] → [Sent] → [Received/Failed]
```

- **Created**: Message created from user input or RAG response
- **Sent**: Message transmitted to backend (user) or RAG system
- **Received**: Response received successfully
- **Failed**: Transmission failed (network error, backend error)

---

## Data Access Patterns

### Authentication Flow

1. **Registration**:
   - INSERT new User record with email and password_hash
   - No session created (redirect to sign-in)

2. **Sign-In**:
   - SELECT User by email
   - VERIFY password_hash using bcrypt
   - INSERT new Session record with session_token and expires_at
   - RETURN session_token as httpOnly cookie

3. **Protected Resource Access**:
   - READ session_token from cookie
   - SELECT Session by token, verify not expired
   - SELECT associated User
   - GRANT access if valid, DENY if invalid (401)

4. **Sign-Out**:
   - DELETE Session record by session_token
   - CLEAR session cookie (expires immediately)

### Chat Flow (Ephemeral)

1. **Send Message**:
   - Verify session token (same as protected resource)
   - Create Message object in-memory
   - Transmit to RAG backend
   - Store Message object in conversation array

2. **Receive Response**:
   - Create Message object (sender='system')
   - Store in conversation array
   - Update UI

3. **Session Expiration**:
   - All in-memory messages/conversations cleared
   - User redirected to sign-in

---

## Security Considerations

### Password Storage

- Hashed using bcrypt with work factor 12
- Salt automatically handled by bcrypt library
- Passwords never logged or stored in plaintext

### Session Tokens

- Cryptographically random (128+ bits)
- Stored as opaque strings (not JWTs to avoid XSS)
- Expire after 7 days (configurable)
- Invalidated on sign-out

### Rate Limiting

- Per-user rate limiting based on user_id from session
- Storage: In-memory for MVP (Redis for scaling)
- Limit: 10 requests/minute per user

### Logging

- Log: Authentication events (sign-in, sign-out, failed), rate limit violations, system errors
- NOT log: Password hashes, session tokens, chat message content, user queries

### CORS

- Allowlist: Vercel frontend origin(s) only
- Credentials: Enabled (required for session cookies)
- Methods: GET, POST, OPTIONS

---

## Scaling Considerations

### Database

- Neon serverless Postgres scales automatically
- Connection pooling via SQLAlchemy for FastAPI
- Indexes on frequently queried columns (user_id, expires_at)

### Rate Limiting

- In-memory storage sufficient for MVP (<100 concurrent users)
- Upgrade to Redis for production scale (>100 concurrent users)

### Session Cleanup

- Cron job or background task to delete expired sessions hourly
- Optional: Cleanup on-demand during sign-in for user-specific sessions
