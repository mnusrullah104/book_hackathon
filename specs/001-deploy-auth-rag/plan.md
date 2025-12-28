# Implementation Plan: Deploy Authenticated RAG Backend and UI

**Branch**: `001-deploy-auth-rag` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-deploy-auth-rag/spec.md`

**Note**: This template is filled in by `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deploy an authenticated RAG chatbot system by integrating Better Auth for user registration/sign-in, deploying the FastAPI backend to Hugging Face Spaces with HTTPS, and connecting the Vercel-deployed Next.js frontend with protected chat endpoints. The system uses session cookies (httpOnly, secure, SameSite) for authentication, enforces per-user rate limiting (10 req/min), and logs authentication events without storing chat content.

## Technical Context

**Language/Version**: Python 3.11+ (FastAPI backend), Next.js 14+ (frontend)
**Primary Dependencies**:
  - Backend: FastAPI, Better Auth (Python), bcrypt/Argon2 (password hashing), slowapi (rate limiting)
  - Frontend: Next.js, Better Auth (Next.js adapter)
  - Infrastructure: Hugging Face Spaces (backend hosting), Vercel (frontend hosting)
**Storage**: Neon Serverless Postgres (free tier per constitution)
**Testing**: pytest (backend), Playwright or Jest + React Testing Library (frontend)
**Target Platform**:
  - Backend: Hugging Face Spaces (Linux/Python environment)
  - Frontend: Vercel (Edge runtime)
**Project Type**: web (backend + frontend)
**Performance Goals**:
  - Message response time: <10 seconds (p95) under normal network conditions
  - Sign-in time: <30 seconds
  - Registration time: <2 minutes
  - Backend uptime: >99%
**Constraints**:
  - Free-tier compatible (Neon Postgres, Hugging Face Spaces)
  - Session cookies: httpOnly, secure, SameSite
  - No chat content logged (privacy)
  - Per-user rate limit: 10 requests/minute
**Scale/Scope**:
  - Single RAG backend instance
  - Email/password authentication only
  - Ephemeral conversations (no persistence beyond session)
  - All authenticated users have equal access (no RBAC)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitution Principle | Status | Rationale |
|---------------------|--------|-----------|
| Spec-first development | PASS | Spec exists with complete requirements, success criteria, and clarifications |
| Technical accuracy and reproducibility | PASS | Plan uses production-ready technologies (FastAPI, Better Auth, Hugging Face, Neon) with documented setup |
| Clarity for developers and AI engineers | PASS | Spec is technology-agnostic, plan provides implementation details with clear examples |
| AI-native architecture (agents, RAG, vector DBs) | PASS | Leverages existing RAG backend with OpenAI Agents/Qdrant per constitution |
| End-to-end transparency | PASS | All deployment steps, environment variables, and observability documented |
| Modular, non-filler content | PASS | Feature scope is bounded (no RBAC, no analytics, no multi-tenant) |

### Post-Design Review (Phase 1 Complete)

All constitutional gates remain PASS. Design artifacts (data-model.md, contracts/, quickstart.md) align with constitution principles:
- Free-tier compatible technologies (Neon Postgres, Hugging Face Spaces)
- Production-quality code examples provided
- Clear documentation structure with traceable requirements

## Project Structure

### Documentation (this feature)

```text
specs/001-deploy-auth-rag/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── backend-api.yaml  # OpenAPI spec for FastAPI endpoints
│   └── auth-flows.md   # Authentication flow documentation
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/                    # FastAPI backend (existing RAG code)
├── src/
│   ├── models/
│   │   ├── user.py         # User model for authentication
│   │   └── session.py      # Session model (if needed)
│   ├── services/
│   │   ├── auth.py         # Authentication service (Better Auth integration)
│   │   └── rag.py          # Existing RAG service (extend with auth)
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py     # Registration, sign-in, sign-out endpoints
│   │   │   └── chat.py    # Protected chat endpoints
│   │   └── middleware/
│   │       ├── auth.py       # Token verification middleware
│   │       └── rate_limit.py # Per-user rate limiting
│   └── main.py            # FastAPI app with CORS and middleware
├── tests/
│   ├── unit/
│   │   └── test_auth.py    # Authentication logic tests
│   └── integration/
│       └── test_api.py       # API endpoint tests
├── requirements.txt
├── Dockerfile              # Hugging Face Spaces deployment
└── README.md               # Backend setup and deployment docs

frontend/                   # Next.js frontend (existing app, already deployed)
├── src/
│   ├── components/
│   │   ├── auth/          # Authentication components
│   │   │   ├── SignInForm.tsx
│   │   │   └── SignUpForm.tsx
│   │   └── chat/          # Chat components
│   │       └── ChatInterface.tsx
│   ├── pages/
│   │   ├── sign-in.tsx
│   │   ├── sign-up.tsx
│   │   └── chat.tsx        # Protected chat page
│   ├── services/
│   │   └── api.ts          # API client with auth token handling
│   └── lib/
│       └── auth.ts          # Better Auth client configuration
├── tests/
│   ├── auth.spec.ts         # Authentication flow tests
│   └── chat.spec.ts         # Chat UI tests
└── .env.local              # Environment variables (Vercel secrets)
```

**Structure Decision**: Web application with backend and frontend in separate directories. Backend extends existing FastAPI RAG code with authentication layer. Frontend extends existing Next.js app (already deployed on Vercel) with Better Auth integration and protected chat page.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations. All architecture decisions align with constitution principles.
