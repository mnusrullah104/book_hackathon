---
id: 001
title: Create RAG Chatbot Backend Spec
stage: spec
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-chatbot-backend
branch: 001-rag-chatbot-backend
user: Muhammad Nasrullah
command: /sp.specify
labels: ["rag", "chatbot", "backend", "fastapi", "specification"]
links:
  spec: specs/001-rag-chatbot-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-rag-chatbot-backend/spec.md
 - specs/001-rag-chatbot-backend/checklists/requirements.md
tests:
 - Validated spec against quality checklist (all items passed)
---

## Prompt

Integrated RAG Chatbot Backend for Vercel Frontend

Project context:
This project is part of a hackathon to build an AI-native textbook using Docusaurus.
The frontend (book UI + chatbot widget) is already deployed on Vercel.
The backend will be a separate FastAPI service that the Vercel frontend communicates with via REST APIs.

Initial instruction:
- Create a new folder named `backend/` at the root of the repository
- All backend code must live inside this folder
- The backend must be deployable independently from the frontend

Target audience:
- Students learning Physical AI & Humanoid Robotics
- Readers of the AI-native textbook
- Hackathon judges evaluating system design and AI integration

Core objective:
Build a Retrieval-Augmented Generation (RAG) chatbot backend that:
1. Answers questions using the full textbook content
2. Answers questions using ONLY user-selected text passed from the frontend
3. Is consumed by a Vercel-hosted frontend through HTTP APIs

Frontend–Backend interaction:
- Frontend (Vercel) sends requests via fetch/axios
- Backend exposes CORS-enabled REST endpoints
- No server-side rendering dependencies on the backend

Mandatory tech stack:
- FastAPI (Python) as backend framework
- OpenAI Agents SDK / ChatKit SDK for chatbot orchestration
- Neon Serverless Postgres for chat history and metadata
- Qdrant Cloud Free Tier for vector embeddings
- Environment-based configuration for production and local use

Functional requirements:
- `/health` endpoint for deployment checks
- `/ingest` endpoint to chunk and embed book markdown content
- `/chat` endpoint for RAG-based Q&A over the entire book
- `/chat/selection` endpoint that strictly limits answers to user-selected text
- Qdrant used for semantic retrieval
- Neon Postgres used for optional persistence (sessions, logs)
- Strict grounding: answers must come only from retrieved content

Deployment requirements:
- Backend must support deployment on:
  - Railway, Fly.io, Render, or similar FastAPI-friendly platforms
- CORS must allow requests from:
  - Vercel frontend domain
  - localhost for development
- No frontend build steps inside backend

Success criteria:
- Frontend on Vercel can successfully call backend APIs
- Chatbot responses are context-aware and grounded
- Selection-based answers do not hallucinate outside the selection
- Vector search works reliably via Qdrant
- Backend is stable, documented, and hackathon-ready

Constraints:
- Language: Python 3.10+
- API style: REST (FastAPI)
- Vector DB: Qdrant Cloud Free Tier
- Database: Neon Serverless Postgres
- Authentication: Optional (bonus scope only)
- Timeline: MVP suitable for hackathon submission

Required folder structure:
backend/
 ├── app/
 │   ├── main.py              # FastAPI app with CORS enabled
 │   ├── api/                 # Route definitions
 │   ├── services/            # RAG + retrieval logic
 │   ├── db/                  # Neon Postgres connection
 │   ├── vectorstore/         # Qdrant client helpers
 │   └── config.py            # Env & settings
 ├── scripts/
 │   └── ingest_book.py       # Run once or on deploy
 ├── requirements.txt
 ├── .env.example
 └── README.md

Explicit non-goals:
- Hosting backend on Vercel (Python not required there)
- Fine-tuning LLMs
- Voice interaction
- Frontend UI components
- Multi-book ingestion

Quality requirements:
- Clean, modular, production-aware code
- Clear comments and docstrings
- Secure handling of API keys via environment variables
- Easy local and cloud deployment

Deliverables:
- Fully functional FastAPI backend
- RAG chatbot connected to Qdrant and Neon
- CORS-enabled APIs consumable by Vercel frontend
- Clear setup and deployment documentation

## Response snapshot

Successfully created feature specification for RAG Chatbot Backend (001-rag-chatbot-backend).

**Branch Created**: `001-rag-chatbot-backend`
**Spec File**: `specs/001-rag-chatbot-backend/spec.md`

**Specification Highlights**:

- 5 prioritized user stories covering full textbook Q&A (P1), selection-based Q&A (P2), content ingestion (P1), chat history (P3), and health monitoring (P1)
- 15 functional requirements (FR-001 through FR-015) covering all API endpoints, data processing, and deployment needs
- 10 measurable success criteria (SC-001 through SC-010) including response times, accuracy metrics, and system reliability
- 3 business outcomes (BO-001 through BO-003) focused on hackathon demonstration and student learning value
- Comprehensive edge cases, assumptions, dependencies, and constraints
- Security considerations covering data protection, access control, and privacy

**Quality Validation**: All checklist items passed
- No implementation details in requirements
- All requirements testable and unambiguous
- Success criteria are measurable and technology-agnostic
- Clear scope boundaries with In Scope / Out of Scope sections
- No [NEEDS CLARIFICATION] markers - all requirements are concrete

**Next Steps**:
- Ready for `/sp.clarify` if targeted questions emerge
- Ready for `/sp.plan` to proceed with architectural design

## Outcome

- ✅ Impact: Complete feature specification created for RAG Chatbot Backend with 5 prioritized user stories, 15 functional requirements, and 10 measurable success criteria
- 🧪 Tests: Spec quality validation checklist created and passed (all items validated)
- 📁 Files: Created spec.md and checklists/requirements.md in specs/001-rag-chatbot-backend/
- 🔁 Next prompts: `/sp.clarify` for additional questions, or `/sp.plan` to begin architectural design
- 🧠 Reflection: Specification successfully captures technical requirements while maintaining user-centric focus. Tech stack constraints (FastAPI, Qdrant, Neon) appropriately placed in Dependencies/Constraints sections per user requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None - spec generation completed successfully with all quality checks passing
- Graders run and results (PASS/FAIL): PASS - All spec quality checklist items validated successfully
- Prompt variant (if applicable): Standard /sp.specify workflow with comprehensive feature description
- Next experiment (smallest change to try): N/A - Ready to proceed to planning phase
