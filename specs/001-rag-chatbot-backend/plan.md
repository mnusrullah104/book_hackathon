# Implementation Plan: RAG Chatbot Backend

**Branch**: `001-rag-chatbot-backend` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot-backend/spec.md`

## Summary

Build a FastAPI backend service that provides Retrieval-Augmented Generation (RAG) capabilities for an AI-native textbook on Physical AI & Humanoid Robotics. The system enables students to ask questions about textbook content through two modes: (1) semantic search across the entire textbook, and (2) strictly grounded answers from user-selected text. The backend integrates with Qdrant Cloud for vector search, Neon Serverless Postgres for chat history persistence, and OpenAI for embeddings and LLM inference.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: FastAPI 0.115.0, OpenAI SDK 1.54.0, Qdrant Client 1.11.0, SQLAlchemy 2.0.35
**Storage**: Neon Serverless Postgres (chat history), Qdrant Cloud (vector embeddings)
**Testing**: pytest, httpx (async testing)
**Target Platform**: Linux server (Render deployment)
**Project Type**: Web (separate backend deployment)
**Performance Goals**: <3s response time for 95% of queries, 50 concurrent users
**Constraints**: <500ms health check response, free tier services only, no hallucination outside context
**Scale/Scope**: 100+ markdown pages, 500+ document chunks, 100+ demo conversations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Constitution Principles Review

✅ **Spec-first development (NON-NEGOTIABLE)**
- Feature begins with formal specification: [spec.md](./spec.md)
- All requirements defined with acceptance criteria
- Traceable from spec → plan → tasks

✅ **Technical accuracy and reproducibility**
- All decisions documented in [research.md](./research.md)
- Configuration via environment variables ([quickstart.md](./quickstart.md))
- Free-tier architecture (Qdrant, Neon, Render free tiers)

✅ **AI-native architecture (agents, RAG, vector DBs)**
- RAG pipeline with Qdrant vector database
- OpenAI embeddings (text-embedding-3-small) and LLM (gpt-4o-mini)
- Grounded responses preventing hallucination

✅ **End-to-end transparency**
- Deployment steps documented in [quickstart.md](./quickstart.md)
- OpenAPI specification in [contracts/openapi.yaml](./contracts/openapi.yaml)
- Environment variables documented in `.env.example`

✅ **Modular, non-filler content**
- Focused backend serving specific endpoints
- Production-quality code patterns
- Clear separation: FastAPI (backend) + Docusaurus (frontend)

### Compliance Status

✅ All gates passed - proceed to implementation

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot-backend/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - Technical decisions
├── data-model.md        # Phase 1 output - Entity definitions
├── quickstart.md        # Phase 1 output - Setup guide
├── contracts/
│   └── openapi.yaml     # Phase 1 output - API specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created yet)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point with CORS
│   ├── config.py            # Environment settings (Pydantic BaseSettings)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py        # GET /health endpoint
│   │   ├── chat.py          # POST /api/chat, GET /api/sessions/{id}
│   │   └── ingest.py        # POST /api/ingest endpoint
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag.py           # RAG pipeline orchestration
│   │   ├── retrieval.py     # Qdrant vector search
│   │   ├── chunking.py      # Markdown chunking logic
│   │   └── embeddings.py    # OpenAI embedding generation
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── session.py       # Database session management
│   │   └── operations.py    # CRUD operations
│   └── vectorstore/
│       ├── __init__.py
│       ├── client.py        # Qdrant client wrapper
│       └── operations.py    # Vector search operations
├── scripts/
│   ├── init_database.py     # One-time Postgres schema setup
│   ├── init_qdrant.py       # One-time Qdrant collection setup
│   └── ingest_book.py       # CLI tool for content ingestion
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_api/
│   │   ├── test_health.py
│   │   ├── test_chat.py
│   │   └── test_ingest.py
│   └── test_services/
│       ├── test_rag.py
│       ├── test_retrieval.py
│       └── test_chunking.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── render.yaml              # Render deployment configuration
```

**Structure Decision**: Web application structure selected because the feature requires a separate backend deployment (FastAPI) from the existing frontend (Docusaurus on Vercel). Backend must be independently deployable with its own runtime, dependencies, and deployment configuration.

## Complexity Tracking

No constitution violations - complexity tracking not required.

---

## Phase 0: Research & Decisions

**Status**: ✅ Complete

**Artifacts**: [research.md](./research.md)

### Key Technical Decisions

1. **Chunking Strategy**: Markdown-aware semantic chunking (512 tokens, 51 overlap)
   - Rationale: Preserves document structure, 85-90% recall, optimal for educational content

2. **Retrieval Configuration**: Top-k=5, similarity threshold=0.7 (0.75 for selection mode)
   - Rationale: Balances context richness with precision, adaptive thresholds prevent hallucination

3. **Selection-Based Grounding**: Hard grounding with explicit citation requirement
   - Rationale: 96% hallucination reduction, meets educational accuracy requirements

4. **Chat History**: Stored sessions in Neon Postgres, stateless API layer
   - Rationale: Enables conversation continuity, horizontal scalability, ACID guarantees

5. **Deployment Platform**: Render (FastAPI-optimized)
   - Rationale: Native ASGI support, flat-rate pricing, auto-deploy from Git

6. **OpenAI Integration**: Direct ChatCompletion API (not Agents SDK)
   - Rationale: Fine-grained control, simpler architecture, better RAG patterns

7. **Embedding Strategy**: text-embedding-3-small (1536 dimensions)
   - Rationale: 6.5x cheaper, sufficient accuracy (75.8%), faster generation

### Research Outcomes

- All "NEEDS CLARIFICATION" items resolved
- Best practices documented with 2025 references
- Cost estimation: ~$9.50 for hackathon demo
- Architecture validated against constitution principles

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

**Artifacts**: [data-model.md](./data-model.md), [contracts/openapi.yaml](./contracts/openapi.yaml), [quickstart.md](./quickstart.md)

### Data Model Summary

**Entities** (5 total):
1. **User**: Textbook reader with session associations
2. **Session**: Conversation thread with mode (full_textbook | selection_only)
3. **Message**: Individual user/assistant messages with retrieval metadata
4. **DocumentChunk**: Indexed textbook segments with embeddings
5. **HealthStatus**: System health monitoring records

**Postgres Schema**:
- 5 tables with referential integrity (CASCADE deletes)
- 5 indexes for query optimization
- 1 trigger (auto-update session last_active)
- JSONB fields for flexible metadata storage

**Qdrant Schema**:
- Collection: `textbook_chunks`
- Dimensions: 1536 (text-embedding-3-small)
- Distance: COSINE (optimal for OpenAI embeddings)
- HNSW index for fast retrieval

### API Contracts Summary

**Endpoints** (3 primary):
1. `GET /health` - Service health check with dependency status
2. `POST /api/chat` - Send message, receive RAG-based response
3. `GET /api/sessions/{id}` - Retrieve conversation history
4. `POST /api/ingest` - Process and index textbook content

**Request/Response Schemas**:
- Defined in OpenAPI 3.1 specification
- JSON request bodies with validation
- Standard HTTP status codes (200, 400, 404, 500, 503)
- CORS-enabled for Vercel frontend

### Quickstart Guide

Complete setup documentation including:
- Environment setup (Python 3.10+, virtual environment)
- External service configuration (OpenAI, Qdrant, Neon)
- Database and vector store initialization
- Content ingestion workflow
- Local development server setup
- API testing examples
- Render deployment instructions
- Troubleshooting guide

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                         │
│              Docusaurus + Chat Widget (React)                │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS + CORS
                  │ REST APIs
                  ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend (Render)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Layer (FastAPI)                      │  │
│  │  /health  |  /api/chat  |  /api/ingest              │  │
│  └────┬─────────────┬─────────────────┬─────────────────┘  │
│       │             │                 │                     │
│  ┌────▼─────────────▼─────────────────▼─────────────────┐  │
│  │           RAG Service Layer                           │  │
│  │  Chunking | Embeddings | Retrieval | LLM Generation  │  │
│  └────┬─────────────┬─────────────────┬─────────────────┘  │
└───────┼─────────────┼─────────────────┼────────────────────┘
        │             │                 │
        ▼             ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Neon        │ │  Qdrant      │ │  OpenAI      │
│  Postgres    │ │  Cloud       │ │  API         │
│  (Free Tier) │ │  (Free Tier) │ │              │
│              │ │              │ │              │
│ Chat History │ │ Vector Store │ │ Embeddings + │
│ Metadata     │ │ Semantic     │ │ LLM (GPT-4o) │
│ Sessions     │ │ Search       │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Data Flow (Full Textbook Mode)

```
1. User Query
   └─> Frontend (Vercel)
       └─> POST /api/chat {mode: "full_textbook", message: "..."}
           └─> FastAPI Backend
               ├─> Retrieve session history (Neon Postgres)
               ├─> Generate query embedding (OpenAI)
               ├─> Vector search top-k=5 (Qdrant, threshold=0.7)
               ├─> Build context (retrieved chunks + history)
               ├─> Generate response (OpenAI ChatCompletion)
               ├─> Store conversation (Neon Postgres)
               └─> Return response {session_id, response, retrieved_chunks}
                   └─> Frontend displays answer
```

### Data Flow (Selection-Only Mode)

```
1. User Highlights Text + Asks Question
   └─> Frontend (Vercel)
       └─> POST /api/chat {mode: "selection_only", selected_text: "...", message: "..."}
           └─> FastAPI Backend
               ├─> NO vector search (hard grounding)
               ├─> Build context (ONLY selected_text)
               ├─> Generate response with strict grounding prompt
               ├─> Store conversation (Neon Postgres)
               └─> Return response {session_id, response, retrieved_chunks: 0}
                   └─> Frontend displays answer
```

### Ingestion Flow

```
1. Textbook Content (Markdown)
   └─> POST /api/ingest {source_dir: "../docs"}
       └─> FastAPI Backend
           ├─> Load markdown files
           ├─> Split by headers (MarkdownHeaderTextSplitter)
           ├─> Chunk with overlap (RecursiveCharacterTextSplitter, 512 tokens)
           ├─> Generate embeddings (OpenAI, batch)
           ├─> Store metadata (Neon Postgres, document_chunks table)
           └─> Index vectors (Qdrant, textbook_chunks collection)
               └─> Return {total_files, total_chunks, ingestion_time}
```

---

## Key Design Patterns

### 1. Repository Pattern (Database Abstraction)

```python
# app/db/operations.py
class SessionRepository:
    async def create_session(self, user_id: UUID, mode: str) -> Session:
        # Create new session with validation
        pass

    async def get_session_history(self, session_id: UUID, limit: int) -> List[Message]:
        # Retrieve conversation messages
        pass

    async def store_message(self, session_id: UUID, role: str, content: str) -> Message:
        # Store message and update session last_active
        pass
```

**Rationale**: Separates data access logic from business logic, enables testing with mock repositories.

### 2. Service Layer Pattern (Business Logic)

```python
# app/services/rag.py
class RAGService:
    def __init__(self, retrieval, embeddings, llm, db):
        self.retrieval = retrieval
        self.embeddings = embeddings
        self.llm = llm
        self.db = db

    async def answer_question(self, query: str, mode: str, session_id: UUID) -> str:
        # Orchestrate RAG pipeline
        if mode == "full_textbook":
            return await self._answer_with_retrieval(query, session_id)
        else:
            return await self._answer_with_selection(query, session_id)
```

**Rationale**: Encapsulates business logic, coordinates multiple dependencies, testable with dependency injection.

### 3. Dependency Injection (FastAPI)

```python
# app/main.py
def get_rag_service() -> RAGService:
    return RAGService(
        retrieval=get_retrieval_service(),
        embeddings=get_embeddings_service(),
        llm=get_llm_service(),
        db=get_db_session()
    )

@app.post("/api/chat")
async def chat(request: ChatRequest, rag: RAGService = Depends(get_rag_service)):
    return await rag.answer_question(request.message, request.mode, request.session_id)
```

**Rationale**: Enables testing with mock dependencies, improves code organization, follows FastAPI best practices.

### 4. Async/Await (Concurrent I/O)

```python
# app/services/embeddings.py
async def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
    # Batch embedding with async OpenAI client
    response = await self.client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    return [item.embedding for item in response.data]
```

**Rationale**: Maximizes throughput for I/O-bound operations (API calls, database queries), essential for FastAPI.

---

## Architectural Decisions Requiring ADR Documentation

Several significant architectural decisions were made during planning that warrant ADR documentation:

📋 **Architectural decision detected: Hard Grounding for Selection-Only Mode**
   - **Impact**: Long-term UX and accuracy implications, affects how students interact with selection feature
   - **Alternatives**: Soft grounding with limited retrieval, no grounding enforcement
   - **Scope**: Cross-cutting, influences prompt design, validation logic, and user expectations
   - **Recommendation**: Document reasoning and tradeoffs? Run `/sp.adr hard-grounding-selection-mode`

📋 **Architectural decision detected: Stored Sessions vs Stateless Architecture**
   - **Impact**: Affects scalability, deployment complexity, and user experience
   - **Alternatives**: Fully stateless (client-managed history), server-side stateful sessions, Redis-only storage
   - **Scope**: Influences database schema, API design, and horizontal scaling strategy
   - **Recommendation**: Document reasoning and tradeoffs? Run `/sp.adr stored-sessions-architecture`

📋 **Architectural decision detected: Direct OpenAI API vs Agents SDK**
   - **Impact**: Determines code complexity, maintainability, and integration patterns
   - **Alternatives**: OpenAI Agents SDK, LangChain, LlamaIndex
   - **Scope**: Cross-cutting, affects all LLM interactions and RAG pipeline design
   - **Recommendation**: Document reasoning and tradeoffs? Run `/sp.adr direct-openai-api-integration`

These decisions should be documented in ADRs after user approval to maintain traceability and architectural clarity.

---

## Non-Functional Requirements

### Performance

- **Response Time**: <3s for 95% of chat queries under normal load
- **Health Check**: <500ms response time
- **Concurrent Users**: Support 50 simultaneous chat sessions without degradation
- **Ingestion**: Process 100 markdown pages in <60 seconds

### Reliability

- **Uptime**: 99% during hackathon demo period
- **Error Handling**: Graceful degradation when dependencies unavailable
- **Data Integrity**: ACID guarantees for chat history (Postgres)
- **Retry Logic**: Exponential backoff for OpenAI API rate limits

### Security

- **API Keys**: Environment variables only, never committed
- **CORS**: Explicit whitelist (Vercel domain + localhost)
- **Input Validation**: Content length limits, SQL injection prevention
- **TLS/SSL**: All external connections encrypted

### Observability

- **Logging**: Structured JSON logs (INFO, ERROR levels)
- **Health Endpoint**: Dependency status monitoring
- **Error Tracking**: Stack traces for debugging
- **Metrics**: Response times, token usage, retrieval counts

---

## Risk Analysis

### Risk 1: OpenAI API Rate Limits

**Probability**: Medium | **Impact**: High

**Mitigation**:
- Implement exponential backoff with retry logic
- Monitor token usage via logging
- Add rate limiting (30 requests/minute per IP)
- Provide clear error messages to users

### Risk 2: Free Tier Service Limits

**Probability**: Medium | **Impact**: Medium

**Mitigation**:
- Qdrant: 1GB storage (sufficient for ~500 chunks)
- Neon: 512MB storage (sufficient for ~1000 conversations)
- Monitor usage via health endpoint
- Document upgrade paths in quickstart guide

### Risk 3: Hallucination in Selection-Only Mode

**Probability**: Low | **Impact**: High

**Mitigation**:
- Hard grounding with explicit system prompt
- Post-generation validation (optional)
- Clear user messaging when answer unavailable
- Extensive testing with edge cases

---

## Testing Strategy

### Unit Tests
- Chunking logic (edge cases: code blocks, math notation)
- Embedding generation (batch processing, error handling)
- Retrieval scoring (similarity thresholds, top-k selection)
- Session management (CRUD operations, validation)

### Integration Tests
- Full RAG pipeline (end-to-end with mock dependencies)
- API endpoints (request validation, response format)
- Database operations (transactions, referential integrity)
- Vector search (Qdrant queries, payload filtering)

### Contract Tests
- OpenAPI schema validation (request/response structures)
- CORS headers (preflight requests, allowed origins)
- Error response formats (consistent error handling)

### Acceptance Tests (Manual)
- Health check returns correct dependency status
- Full textbook mode retrieves relevant chunks
- Selection mode answers only from provided text
- Session history persists across requests
- Ingestion indexes all markdown content

---

## Deployment Strategy

### Local Development
1. Set up Python virtual environment
2. Configure `.env` with API keys
3. Initialize Postgres schema (`init_database.py`)
4. Initialize Qdrant collection (`init_qdrant.py`)
5. Ingest textbook content (`ingest_book.py`)
6. Start uvicorn server (`uvicorn app.main:app --reload`)

### Production Deployment (Render)
1. Push code to GitHub branch
2. Create Render web service from repository
3. Configure environment variables in Render dashboard
4. Deploy automatically via Render's build process
5. Run post-deploy scripts (database init, content ingestion)
6. Verify health endpoint returns 200 status
7. Update Vercel frontend with backend URL

### Rollback Strategy
- Render supports instant rollback to previous deployment
- Database migrations use Alembic for version control
- Qdrant collections can be recreated from source markdown

---

## Definition of Done

✅ All API endpoints implemented and tested
✅ OpenAPI specification matches implementation
✅ Health endpoint returns correct dependency status
✅ Full textbook mode retrieves relevant chunks (similarity >0.7)
✅ Selection mode answers only from provided text (zero hallucination)
✅ Chat history persists and retrieves correctly
✅ Ingestion processes 100+ pages without errors
✅ Deployed to Render with public HTTPS endpoint
✅ Frontend integration verified (CORS, API calls)
✅ Documentation complete (README, quickstart, API docs)
✅ Constitution compliance verified (all principles met)

---

## Next Steps

1. **Generate Tasks** (`/sp.tasks`): Break down implementation plan into atomic, testable tasks
2. **Create ADRs** (optional): Document key architectural decisions identified above
3. **Begin Implementation** (`/sp.implement`): Execute tasks in dependency order
4. **Testing & Validation**: Verify all acceptance criteria met
5. **Deployment**: Deploy to Render and integrate with Vercel frontend

---

## References

- Feature Specification: [spec.md](./spec.md)
- Technical Research: [research.md](./research.md)
- Data Model: [data-model.md](./data-model.md)
- API Contracts: [contracts/openapi.yaml](./contracts/openapi.yaml)
- Setup Guide: [quickstart.md](./quickstart.md)
- Constitution: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)
