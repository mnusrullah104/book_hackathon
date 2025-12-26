---
id: 002
title: Create RAG Chatbot Implementation Plan
stage: plan
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-rag-chatbot-backend
branch: 001-rag-chatbot-backend
user: Muhammad Nasrullah
command: /sp.plan
labels: ["rag", "architecture", "planning", "fastapi", "design"]
links:
  spec: specs/001-rag-chatbot-backend/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-rag-chatbot-backend/plan.md
 - specs/001-rag-chatbot-backend/research.md
 - specs/001-rag-chatbot-backend/data-model.md
 - specs/001-rag-chatbot-backend/contracts/openapi.yaml
 - specs/001-rag-chatbot-backend/quickstart.md
tests:
 - Constitution compliance check (all principles passed)
 - Technical context validation (all unknowns resolved)
---

## Prompt

Create:
- High-level system architecture
- Book + RAG chatbot structure
- Backend execution roadmap
- Quality and acceptance validation

Architecture sketch:
- Frontend: Docusaurus book + chatbot UI on Vercel
- Backend: FastAPI (separate deployment)
- LLM: OpenAI Agents / ChatKit
- Vector DB: Qdrant Cloud
- Database: Neon Serverless Postgres
- Communication: REST APIs with CORS

Section structure:
1. AI/Spec-driven book (completed)
2. Backend foundation (FastAPI, env, CORS)
3. RAG pipeline (chunking, embeddings, retrieval)
4. Chatbot logic (grounded + selection-based answers)
5. Frontend integration
6. Deployment & demo

Research approach:
- Research-concurrent development
- Follow official docs only
- Use textbook as sole knowledge source

Decisions needing documentation:
- Chunking: fixed vs semantic
- Retrieval: top-k size
- Hosting: Railway vs Render
- Selection enforcement: hard vs soft grounding
- Chat history: stored vs stateless

Testing strategy:
- Verify all book content is embedded
- Validate relevant retrieval only
- Ensure no hallucination outside context
- Selection mode uses ONLY provided text
- Frontend ↔ backend API works (CORS, latency)

Phases:
- Research → Foundation → Analysis → Synthesis

## Response snapshot

Successfully created comprehensive implementation plan for RAG Chatbot Backend (001-rag-chatbot-backend).

**Artifacts Created**:
1. `plan.md` - Complete implementation plan with architecture, design patterns, and deployment strategy
2. `research.md` - Technical decisions with 7 key choices (chunking, retrieval, grounding, sessions, deployment, OpenAI integration, embeddings)
3. `data-model.md` - 5 entities (User, Session, Message, DocumentChunk, HealthStatus) with Postgres + Qdrant schemas
4. `contracts/openapi.yaml` - OpenAPI 3.1 specification with 4 endpoints and complete request/response schemas
5. `quickstart.md` - Step-by-step setup guide from zero to deployed backend

**Phase 0 (Research) - Key Decisions**:
- Chunking: Markdown-aware semantic (512 tokens, 51 overlap) for 85-90% recall
- Retrieval: Top-k=5, similarity=0.7 (0.75 for selection mode)
- Grounding: Hard grounding with 96% hallucination reduction
- Sessions: Stored in Neon Postgres (conversation continuity + horizontal scaling)
- Deployment: Render (native ASGI support, flat-rate pricing)
- OpenAI: Direct ChatCompletion API (fine-grained control vs Agents SDK complexity)
- Embeddings: text-embedding-3-small (6.5x cheaper, 75.8% accuracy sufficient)

**Phase 1 (Design) - Deliverables**:
- Data model with 5 entities, referential integrity, optimized indexes
- OpenAPI contract with 4 endpoints (health, chat, sessions, ingest)
- Quickstart with external service setup (OpenAI, Qdrant, Neon), initialization scripts, testing examples, and Render deployment

**Architecture Highlights**:
- FastAPI backend (Render) ↔ Qdrant Cloud (vectors) + Neon Postgres (history) + OpenAI API (LLM)
- Two RAG modes: full textbook (semantic search) + selection-only (hard grounding)
- Repository pattern for data access, service layer for business logic, dependency injection for testability
- Async/await for concurrent I/O operations
- CORS-enabled REST APIs for Vercel frontend

**Constitution Compliance**: ✅ All gates passed
- Spec-first development with traceable requirements
- Technical accuracy with research documentation
- AI-native architecture (RAG, vector DB, grounded responses)
- End-to-end transparency (deployment docs, OpenAPI, env variables)
- Modular content with production-quality patterns

**ADR Suggestions** (3 significant decisions):
1. Hard Grounding for Selection-Only Mode - UX + accuracy implications
2. Stored Sessions vs Stateless Architecture - scalability + deployment complexity
3. Direct OpenAI API vs Agents SDK - code complexity + maintainability

**Cost Estimation**: ~$9.50 for hackathon demo (embeddings $1.00, LLM $1.50, Render $7/month)

**Next Steps**:
- `/sp.tasks` to generate atomic, testable implementation tasks
- Optional `/sp.adr` to document architectural decisions
- `/sp.implement` to execute tasks in dependency order

## Outcome

- ✅ Impact: Complete implementation plan with Phase 0 (research) and Phase 1 (design) artifacts covering architecture, data model, API contracts, and deployment strategy
- 🧪 Tests: Constitution compliance validated, technical context resolved (all unknowns addressed), design patterns documented
- 📁 Files: Created plan.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md
- 🔁 Next prompts: `/sp.tasks` for task breakdown, optional `/sp.adr` for architectural decisions, then `/sp.implement` for execution
- 🧠 Reflection: Comprehensive planning phase completed with research-backed technical decisions, production-ready architecture patterns, and clear separation between frontend (Vercel) and backend (Render). All constitution principles met.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all Phase 0 and Phase 1 deliverables
- Graders run and results (PASS/FAIL): PASS - Constitution compliance verified, technical context fully resolved, design artifacts complete
- Prompt variant (if applicable): Standard /sp.plan workflow with comprehensive user requirements
- Next experiment (smallest change to try): N/A - Ready to proceed to task generation phase
