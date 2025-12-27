# Research: Deploy Authenticated RAG Backend and UI

**Feature**: [001-deploy-auth-rag](./spec.md)
**Date**: 2025-12-27
**Purpose**: Document technical decisions and research findings for architectural design

## Authentication Architecture

### Decision: Better Auth for FastAPI + Next.js

**Chosen**: Better Auth with separate adapters:
  - Backend: Python adapter (custom implementation or FastAPI-compatible library)
  - Frontend: Next.js adapter (official Better Auth SDK)

**Rationale**:
  - Better Auth provides modern session-based authentication with httpOnly, secure, SameSite cookies (spec requirement)
  - Session cookies are more secure than JWTs (no XSS vulnerability, automatic expiration)
  - Better Auth supports both Python and JavaScript ecosystems
  - Alignment with constitution's "AI-native architecture" - modern, production-ready

**Alternatives considered**:
  - JWT with localStorage storage: Rejected due to XSS vulnerability (cookies httpOnly)
  - Auth0/NextAuth: More complex, requires third-party service dependency
  - Custom session implementation: Higher maintenance burden, reinventing wheel

### Decision: Password Hashing Algorithm

**Chosen**: bcrypt (via bcrypt library)

**Rationale**:
  - Industry standard with proven security record
  - Better Auth default/recommended
  - Balanced between security and performance (computational cost adjustable via work factor)
  - Widely supported in Python and Node.js ecosystems

**Alternatives considered**:
  - Argon2: More secure but slower computational overhead (may impact sign-in performance)
  - scrypt: Similar to Argon2, less common
  - PBKDF2: Weaker than bcrypt

**Configuration**:
  - Work factor: 12 rounds (balance between security and performance for 30-second sign-in goal)

## Backend Deployment

### Decision: Hugging Face Spaces with Docker

**Chosen**: Hugging Face Spaces (Docker runtime) for FastAPI deployment

**Rationale**:
  - Free tier available (constitution requirement)
  - Automatic HTTPS provided
  - Python environment with GPU support (for RAG acceleration if needed)
  - Easy deployment via git push or web UI
  - Public URL for frontend integration

**Alternatives considered**:
  - Railway/Render: Good alternatives but Hugging Face chosen per spec requirement
  - AWS Lambda: More complex setup, cold starts
  - DigitalOcean Droplet: Manual HTTPS setup required

**Docker Configuration**:
  - Base image: python:3.11-slim
  - Port: 7860 (Hugging Face default)
  - Health check endpoint: `/health`
  - Environment variables: Database URL, secret key, CORS origins

### Decision: CORS Configuration

**Chosen**: Explicit allowlist of frontend origins via FastAPI CORSMiddleware

**Rationale**:
  - Explicit origins more secure than wildcard `*` (prevents CSRF)
  - Vercel frontend URL known (e.g., `https://your-app.vercel.app`)
  - Supports credentials (cookies) with `allow_credentials=True`

**Configuration**:
  - `allow_origins`: Vercel deployment URL(s)
  - `allow_credentials`: True (required for session cookies)
  - `allow_methods`: `["GET", "POST", "OPTIONS"]`
  - `allow_headers`: `["Content-Type", "Authorization"]`

## Rate Limiting

### Decision: Per-User Rate Limiting with slowapi

**Chosen**: slowapi library with in-memory storage and user-based keys

**Rationale**:
  - Built specifically for FastAPI
  - Supports function-level decorators for granular control
  - Per-user keys from authentication token (spec requirement: 10 req/min)
  - Simple configuration with Redis option for scaling (future)

**Alternatives considered**:
  - Flask-Limiter: Flask-specific, not FastAPI
  - Custom middleware: Higher implementation burden
  - Cloudflare rate limiting: External service, not needed for MVP

**Configuration**:
  - Backend rate limit: 10 requests/minute per user
  - Strategy: `Limiter(key_func=get_user_identifier)`
  - Storage: In-memory (sufficient for MVP; Redis for scaling)
  - On exceeded: Return 429 Too Many Requests with Retry-After header

## Database

### Decision: Neon Serverless Postgres

**Chosen**: Neon Serverless Postgres (free tier per constitution)

**Rationale**:
  - Free tier available (constitution requirement)
  - Serverless: scales automatically, no manual scaling needed
  - PostgreSQL with pgvector extension (for vector storage if needed)
  - Connection pooling for FastAPI integration
  - Compatible with Better Auth schema requirements

**Alternatives considered**:
  - Supabase: Also good, but Neon chosen per constitution
  - SQLite: No network access from Hugging Face Spaces (file-based only)
  - MongoDB: Not in constitution's recommended stack

**Schema Requirements**:
  - Users table: id, email, password_hash, created_at
  - Sessions table: id, user_id, session_token, expires_at (if Better Auth requires custom storage)

## Session Management

### Decision: Session Cookies (httpOnly, Secure, SameSite)

**Chosen**: Better Auth session cookies with hardened security attributes

**Rationale**:
  - Spec requirement explicitly states session cookies
  - httpOnly: Prevents JavaScript access (XSS protection)
  - Secure: Enforces HTTPS-only transmission
  - SameSite=Lax: Balances CSRF protection with cross-site navigation
  - Better Auth handles cookie rotation and expiration automatically

**Cookie Configuration**:
  - `httpOnly`: True
  - `secure`: True (HTTPS only)
  - `sameSite`: "lax" (allows top-level navigation)
  - `maxAge`: 7 days (balance security and UX)
  - Domain: None (default to current domain, works cross-origin with CORS)

## Logging

### Decision: Structured Logging with Python Logging Module

**Chosen**: Python `logging` module with structured JSON format

**Rationale**:
  - Built-in, no additional dependencies
  - Structured format便于 parsing and analysis
  - Meets spec requirement: auth events + errors only
  - No chat content logged (privacy requirement)

**Log Events**:
  - Sign-in success: `user_id`, `email`, `timestamp`, `ip_address`
  - Sign-in failure: `email`, `reason` (invalid credentials), `timestamp`, `ip_address`
  - Sign-out: `user_id`, `timestamp`
  - Rate limit exceeded: `user_id`, `timestamp`
  - System errors: `error_type`, `error_message`, `stack_trace`, `timestamp`
  - NOT logged: Chat message content, RAG responses, user queries

**Storage**:
  - Local stdout/stderr (Hugging Face Spaces logs accessible via UI)
  - Future: Optional external log aggregation (e.g., LogRocket, Datadog)

## Security Headers

### Decision: FastAPI Security Headers Middleware

**Chosen**: Explicit security headers via FastAPI middleware

**Rationale**:
  - Complements httpOnly cookies for defense-in-depth
  - Prevents MIME sniffing, clickjacking, XSS
  - Standard security best practices

**Headers**:
  - `X-Content-Type-Options`: nosniff
  - `X-Frame-Options`: DENY
  - `X-XSS-Protection`: 1; mode=block
  - `Strict-Transport-Security`: max-age=31536000; includeSubDomains (HSTS)
  - `Content-Security-Policy`: restrictive policy for production

## Frontend Integration

### Decision: Better Auth Next.js SDK

**Chosen**: Official Better Auth SDK for Next.js 14+ with App Router

**Rationale**:
  - Native Next.js integration
  - Server components support
  - Session cookie handling automatic
  - Server actions for secure auth operations

**Configuration**:
  - Base URL: Hugging Face Spaces backend URL
  - Session management: Automatic via cookies
  - Protected routes: Middleware wrapper for server components

## Open Questions for Planning

The following items require planning phase decisions but have no blocking research gaps:

1. **Better Auth Python adapter**: No official Python adapter exists. Decision needed: Use Better Auth REST API from Python, or implement custom session management compatible with Next.js SDK?
   - **Recommendation**: Use Next.js Better Auth SDK with custom FastAPI endpoints that share session cookie secret. FastAPI validates session tokens from cookie.

2. **Hugging Face Spaces free tier limits**: Documentation shows ~16GB RAM, 8 vCPU limits. May impact RAG query performance.
   - **Mitigation**: Monitor latency in SC-003 (<10 seconds). If exceeded, upgrade to paid tier.

3. **Session storage**: Better Auth typically uses database for sessions. Need to determine if in-memory sessions acceptable for MVP (simpler) or database storage required (more robust).
   - **Recommendation**: Database sessions via Neon Postgres for reliability and scalability.

## Summary

All critical technical decisions documented. Architecture is:
  - FastAPI backend on Hugging Face Spaces with Better Auth-compatible session management
  - Next.js frontend on Vercel with Better Auth SDK
  - Neon Serverless Postgres for user/session storage
  - Session cookies (httpOnly, secure, SameSite) for authentication
  - Per-user rate limiting via slowapi
  - CORS allowlist for frontend origin
  - Structured logging (auth events + errors only, no chat content)

Next phase: Generate data model, API contracts, and quickstart guide.
