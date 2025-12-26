# Tasks: RAG Chatbot Backend

**Input**: Design documents from `/specs/001-rag-chatbot-backend/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are EXCLUDED per policy.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

Per plan.md, this is a web application with separate backend deployment:
- Backend paths: `backend/app/`, `backend/scripts/`, `backend/tests/`
- Configuration files: `backend/requirements.txt`, `backend/.env.example`, `backend/README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend/ directory structure per plan.md (app/, scripts/, tests/ subdirectories)
- [ ] T002 Initialize Python project with requirements.txt (FastAPI 0.115.0, OpenAI 1.54.0, Qdrant 1.11.0, SQLAlchemy 2.0.35, pytest, httpx)
- [ ] T003 [P] Create backend/.env.example with required environment variables (OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL, ALLOWED_ORIGINS)
- [ ] T004 [P] Create backend/.gitignore for Python project (.env, __pycache__/, *.pyc, venv/)
- [ ] T005 [P] Create backend/README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create backend/app/__init__.py (empty module initializer)
- [ ] T007 Create backend/app/config.py with Pydantic BaseSettings for environment configuration
- [ ] T008 Create backend/app/main.py with FastAPI app initialization and CORS middleware configuration
- [ ] T009 [P] Create backend/app/db/__init__.py (empty module initializer)
- [ ] T010 [P] Create backend/app/db/models.py with SQLAlchemy ORM models (User, Session, Message, DocumentChunk, HealthStatus per data-model.md)
- [ ] T011 [P] Create backend/app/db/session.py with async database session management (Neon Postgres connection)
- [ ] T012 [P] Create backend/app/db/operations.py with repository pattern CRUD operations (create_session, get_session_history, store_message)
- [ ] T013 [P] Create backend/app/vectorstore/__init__.py (empty module initializer)
- [ ] T014 [P] Create backend/app/vectorstore/client.py with Qdrant async client wrapper
- [ ] T015 [P] Create backend/app/vectorstore/operations.py with vector search operations (semantic_search, index_chunks)
- [ ] T016 [P] Create backend/app/api/__init__.py (empty module initializer)
- [ ] T017 Create backend/scripts/init_database.py for one-time Postgres schema setup (tables, indexes, triggers per data-model.md)
- [ ] T018 [P] Create backend/scripts/init_qdrant.py for one-time Qdrant collection setup (textbook_chunks collection, 1536 dimensions, COSINE distance)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 5 - Health Check & Monitoring (Priority: P1) 🎯 MVP Foundation

**Goal**: Verify backend service is running correctly with dependency health checks

**Independent Test**: Call `/health` endpoint and verify it returns 200 status with healthy state for all components (Qdrant, Postgres, OpenAI)

**Why First**: This is the simplest P1 story and provides immediate deployment verification. Essential for confirming foundational infrastructure before implementing complex RAG features.

### Implementation for User Story 5

- [ ] T019 [US5] Create backend/app/api/health.py with GET /health endpoint that checks Qdrant connectivity
- [ ] T020 [US5] Add Neon Postgres connectivity check to backend/app/api/health.py
- [ ] T021 [US5] Add OpenAI API availability check to backend/app/api/health.py
- [ ] T022 [US5] Return JSON response with service_status, dependencies (qdrant/postgres/openai), and response_time_ms in backend/app/api/health.py
- [ ] T023 [US5] Register health router in backend/app/main.py
- [ ] T024 [US5] Add error handling for degraded/unhealthy states (return 503 status) in backend/app/api/health.py

**Checkpoint**: Health endpoint functional - can deploy and verify backend is running

---

## Phase 4: User Story 3 - Content Ingestion (Priority: P1) 🎯 MVP Prerequisite

**Goal**: Process and index textbook content for semantic search

**Independent Test**: Call `/api/ingest` with textbook markdown directory and verify chunks are stored in Qdrant with proper embeddings

**Why Second**: Must complete before US1 (Full Textbook Q&A) can function. Provides the knowledge base for RAG retrieval.

### Implementation for User Story 3

- [ ] T025 [P] [US3] Create backend/app/services/__init__.py (empty module initializer)
- [ ] T026 [P] [US3] Create backend/app/services/chunking.py with MarkdownHeaderTextSplitter (split by #, ##, ###)
- [ ] T027 [US3] Add RecursiveCharacterTextSplitter to backend/app/services/chunking.py (512 tokens, 51 overlap per research.md)
- [ ] T028 [US3] Implement chunk_markdown function in backend/app/services/chunking.py that preserves code blocks and math notation
- [ ] T029 [P] [US3] Create backend/app/services/embeddings.py with async OpenAI embedding generation (text-embedding-3-small, 1536 dimensions)
- [ ] T030 [US3] Implement batch embedding function in backend/app/services/embeddings.py (batch size up to 2048 chunks)
- [ ] T031 [US3] Create backend/app/api/ingest.py with POST /api/ingest endpoint
- [ ] T032 [US3] Implement file loading logic in backend/app/api/ingest.py (read markdown files from source_dir)
- [ ] T033 [US3] Integrate chunking service in backend/app/api/ingest.py (call chunk_markdown for each file)
- [ ] T034 [US3] Integrate embedding service in backend/app/api/ingest.py (generate embeddings for all chunks)
- [ ] T035 [US3] Store chunk metadata in Neon Postgres (document_chunks table) via backend/app/db/operations.py
- [ ] T036 [US3] Index vectors in Qdrant (textbook_chunks collection) via backend/app/vectorstore/operations.py
- [ ] T037 [US3] Register ingest router in backend/app/main.py
- [ ] T038 [US3] Add error handling for malformed markdown files in backend/app/api/ingest.py
- [ ] T039 [US3] Return ingestion summary (total_files, total_chunks, ingestion_time_seconds) in backend/app/api/ingest.py
- [ ] T040 [US3] Create backend/scripts/ingest_book.py CLI tool for command-line content ingestion

**Checkpoint**: Content ingestion functional - textbook can be indexed for semantic search

---

## Phase 5: User Story 1 - Full Textbook Q&A (Priority: P1) 🎯 MVP Core

**Goal**: Answer student questions using semantic search across entire textbook

**Independent Test**: Send question "What is inverse kinematics?" via `/api/chat` and verify response contains relevant textbook content with proper context grounding

**Why Third**: Core RAG functionality. Depends on US3 (ingestion) being complete. This is the primary value delivery for MVP.

### Implementation for User Story 1

- [ ] T041 [P] [US1] Create backend/app/services/retrieval.py with semantic_search function (top-k=5, similarity_threshold=0.7 per research.md)
- [ ] T042 [US1] Implement query embedding generation in backend/app/services/retrieval.py (reuse embeddings service)
- [ ] T043 [US1] Implement Qdrant vector search in backend/app/services/retrieval.py (COSINE distance, return top chunks with metadata)
- [ ] T044 [P] [US1] Create backend/app/services/rag.py with RAGService class (orchestrates retrieval + LLM generation)
- [ ] T045 [US1] Implement context building in backend/app/services/rag.py (combine retrieved chunks + chat history)
- [ ] T046 [US1] Implement LLM generation in backend/app/services/rag.py using OpenAI ChatCompletion (gpt-4o-mini, temperature=0.3)
- [ ] T047 [US1] Add system prompt for full textbook mode in backend/app/services/rag.py (grounded responses, cite sources)
- [ ] T048 [US1] Implement answer_with_retrieval method in backend/app/services/rag.py (full pipeline: embed query → search → build context → generate)
- [ ] T049 [US1] Create backend/app/api/chat.py with POST /api/chat endpoint
- [ ] T050 [US1] Implement session creation/retrieval logic in backend/app/api/chat.py (auto-generate UUID if no session_id provided)
- [ ] T051 [US1] Integrate RAGService for full_textbook mode in backend/app/api/chat.py
- [ ] T052 [US1] Store user message and assistant response in Postgres via backend/app/db/operations.py
- [ ] T053 [US1] Return ChatResponse with session_id, message_id, response, retrieved_chunks count in backend/app/api/chat.py
- [ ] T054 [US1] Register chat router in backend/app/main.py
- [ ] T055 [US1] Add validation for full_textbook mode requests (message required, max 5000 chars) in backend/app/api/chat.py
- [ ] T056 [US1] Handle case where no relevant content found (return "information not available" message) in backend/app/services/rag.py
- [ ] T057 [US1] Add error handling for OpenAI API failures (rate limits, timeouts) with retry logic in backend/app/services/rag.py

**Checkpoint**: Full textbook Q&A functional - core MVP feature complete

---

## Phase 6: User Story 2 - Selection-Based Q&A (Priority: P2)

**Goal**: Answer questions strictly based on user-selected text (hard grounding)

**Independent Test**: Send highlighted text with question to `/api/chat` (mode=selection_only) and verify answer references ONLY the provided selection

### Implementation for User Story 2

- [ ] T058 [US2] Add SELECTION_ONLY_PROMPT system prompt to backend/app/services/rag.py (hard grounding rules, cite from selection only)
- [ ] T059 [US2] Implement answer_with_selection method in backend/app/services/rag.py (NO vector search, context = selected_text only)
- [ ] T060 [US2] Add mode-based routing in backend/app/api/chat.py (if mode=selection_only, call answer_with_selection)
- [ ] T061 [US2] Add validation for selection_only mode (selected_text required, max 10000 chars) in backend/app/api/chat.py
- [ ] T062 [US2] Store selected_text in session metadata (JSONB field) via backend/app/db/operations.py
- [ ] T063 [US2] Return retrieved_chunks=0 for selection mode responses in backend/app/api/chat.py
- [ ] T064 [US2] Add fallback response for insufficient context in backend/app/services/rag.py ("cannot answer based on selection alone")

**Checkpoint**: Selection-based Q&A functional - both RAG modes working

---

## Phase 7: User Story 4 - Chat History Persistence (Priority: P3)

**Goal**: Enable conversation continuity across sessions

**Independent Test**: Conduct conversation, close session, retrieve history via GET `/api/sessions/{id}` and verify all messages are present

### Implementation for User Story 4

- [ ] T065 [US4] Create GET /api/sessions/{session_id} endpoint in backend/app/api/chat.py
- [ ] T066 [US4] Implement get_session_history function in backend/app/db/operations.py (retrieve messages with pagination)
- [ ] T067 [US4] Add query parameters for pagination (limit=50, offset=0) in backend/app/api/chat.py
- [ ] T068 [US4] Return SessionHistoryResponse with session metadata and messages array in backend/app/api/chat.py
- [ ] T069 [US4] Add session not found error handling (return 404) in backend/app/api/chat.py
- [ ] T070 [US4] Update RAGService to include chat history in context (last 5 messages) via backend/app/services/rag.py

**Checkpoint**: Chat history persistence functional - all user stories complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T071 [P] Add rate limiting middleware to backend/app/main.py (30 requests/minute per IP using slowapi)
- [ ] T072 [P] Add structured logging to all services in backend/app/services/ (INFO level for operations, ERROR for failures)
- [ ] T073 [P] Create backend/render.yaml for Render deployment configuration (build command, start command, health check path)
- [ ] T074 [P] Update backend/README.md with quickstart instructions, API documentation, and deployment guide
- [ ] T075 [P] Add input sanitization for all API endpoints (prevent SQL injection, XSS) in backend/app/api/
- [ ] T076 Add exponential backoff for OpenAI API retries in backend/app/services/embeddings.py and backend/app/services/rag.py
- [ ] T077 [P] Add response time logging for all API endpoints in backend/app/main.py
- [ ] T078 Verify all acceptance scenarios from spec.md work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 5 - Health Check (Phase 3)**: Depends on Foundational - No dependencies on other stories
- **User Story 3 - Ingestion (Phase 4)**: Depends on Foundational - BLOCKS User Story 1
- **User Story 1 - Full Q&A (Phase 5)**: Depends on Foundational + US3 completion
- **User Story 2 - Selection Q&A (Phase 6)**: Depends on Foundational + US1 completion (reuses RAG infrastructure)
- **User Story 4 - History (Phase 7)**: Depends on Foundational + US1 completion (enhances existing chat)
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ├─→ US5: Health Check (Phase 3) ✓ Independent
    ├─→ US3: Ingestion (Phase 4) ✓ Independent
    │      └─→ US1: Full Q&A (Phase 5) ✓ Requires US3 data
    │             ├─→ US2: Selection Q&A (Phase 6) ✓ Reuses US1 infrastructure
    │             └─→ US4: History (Phase 7) ✓ Enhances US1 chat
    └─→ Polish (Phase 8)
```

### MVP Scope

**Minimum Viable Product (Phases 1-5)**:
- Phase 1: Setup
- Phase 2: Foundational
- Phase 3: US5 (Health Check)
- Phase 4: US3 (Ingestion)
- Phase 5: US1 (Full Q&A)

This MVP delivers:
✅ Deployable backend with health monitoring
✅ Textbook content indexed and searchable
✅ Students can ask questions and get grounded answers
✅ Ready for hackathon demo

**Enhanced MVP (Add Phase 6)**: Adds selection-based Q&A for focused explanations

**Full Feature Set (All Phases)**: Adds conversation history for multi-turn interactions

### Within Each User Story

- **US5 (Health)**: Health checks → Error handling → Registration (sequential)
- **US3 (Ingestion)**: Chunking & Embeddings services in parallel → Ingestion endpoint → CLI tool
- **US1 (Full Q&A)**: Retrieval & RAGService can start in parallel → Chat endpoint → Validation/Error handling
- **US2 (Selection)**: Builds on US1 infrastructure, mostly sequential
- **US4 (History)**: Builds on US1 infrastructure, mostly sequential

### Parallel Opportunities

**Phase 1 (Setup)**: T003, T004, T005 (all [P]) can run in parallel

**Phase 2 (Foundational)**:
- T009-T012 (database layer) can run in parallel
- T013-T015 (vector store layer) can run in parallel
- T016 (API module init) can run in parallel
- T017-T018 (init scripts) can run in parallel

**Phase 4 (US3 - Ingestion)**:
- T025-T026 (services init + chunking) can start in parallel
- T029 (embeddings) can run in parallel with chunking

**Phase 5 (US1 - Full Q&A)**:
- T041-T043 (retrieval) and T044 (RAG service) can start in parallel

**Phase 8 (Polish)**:
- T071, T072, T073, T074, T075, T077 (all [P]) can run in parallel

---

## Parallel Example: User Story 1 (Full Q&A)

```bash
# Launch retrieval and RAG service setup in parallel:
Task: "Create backend/app/services/retrieval.py with semantic_search function"
Task: "Create backend/app/services/rag.py with RAGService class"

# After retrieval is done, implement Qdrant vector search:
Task: "Implement Qdrant vector search in backend/app/services/retrieval.py"

# After RAG service is created, build LLM generation:
Task: "Implement LLM generation in backend/app/services/rag.py using OpenAI ChatCompletion"
```

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all foundational components in parallel:
Task: "Create backend/app/db/models.py with SQLAlchemy ORM models"
Task: "Create backend/app/db/session.py with async database session management"
Task: "Create backend/app/db/operations.py with repository pattern CRUD operations"
Task: "Create backend/app/vectorstore/client.py with Qdrant async client wrapper"
Task: "Create backend/app/vectorstore/operations.py with vector search operations"
Task: "Create backend/scripts/init_database.py for Postgres schema setup"
Task: "Create backend/scripts/init_qdrant.py for Qdrant collection setup"
```

---

## Implementation Strategy

### MVP First (Phases 1-5 Only)

1. Complete Phase 1: Setup → Project structure ready
2. Complete Phase 2: Foundational → Infrastructure ready
3. Complete Phase 3: US5 (Health Check) → Deployment verification ready
4. Complete Phase 4: US3 (Ingestion) → Knowledge base ready
5. Complete Phase 5: US1 (Full Q&A) → Core RAG functionality ready
6. **STOP and VALIDATE**: Test full textbook Q&A independently
7. Deploy to Render and integrate with Vercel frontend
8. Hackathon demo ready!

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Backend infrastructure deployed
2. **Health Check** (Phase 3) → Monitoring active, deployment verified
3. **Ingestion** (Phase 4) → Textbook indexed, semantic search ready
4. **Full Q&A** (Phase 5) → **MVP COMPLETE** - Core value delivered
5. **Selection Q&A** (Phase 6) → Enhanced learning workflows
6. **History** (Phase 7) → Conversation continuity
7. **Polish** (Phase 8) → Production hardening

Each increment is independently deployable and adds value.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Phases 1-2 together** (foundation must be solid)
2. **Once Foundational is done**:
   - Developer A: Phase 3 (US5 - Health)
   - Developer B: Phase 4 (US3 - Ingestion)
3. **After US3 completes**:
   - Developer A or B: Phase 5 (US1 - Full Q&A)
4. **After US1 completes**:
   - Developer C: Phase 6 (US2 - Selection Q&A)
   - Developer D: Phase 7 (US4 - History)
5. **All devs**: Phase 8 (Polish in parallel)

---

## Task Count Summary

- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (Foundational)**: 13 tasks (BLOCKING)
- **Phase 3 (US5 - Health)**: 6 tasks
- **Phase 4 (US3 - Ingestion)**: 16 tasks
- **Phase 5 (US1 - Full Q&A)**: 17 tasks
- **Phase 6 (US2 - Selection)**: 7 tasks
- **Phase 7 (US4 - History)**: 6 tasks
- **Phase 8 (Polish)**: 8 tasks

**Total**: 78 tasks

**MVP (Phases 1-5)**: 57 tasks
**Enhanced MVP (+Phase 6)**: 64 tasks
**Full Feature (+Phases 6-7)**: 70 tasks
**Production Ready (+Phase 8)**: 78 tasks

---

## Notes

- All task IDs follow sequential numbering (T001-T078)
- [P] markers indicate parallelizable tasks (different files, no dependencies)
- [Story] labels (US1-US5) map tasks to specific user stories for traceability
- Each user story phase is independently testable as specified in spec.md
- Tests are EXCLUDED per specification (no TDD approach requested)
- File paths use backend/ prefix per plan.md web application structure
- Constitution compliance: Spec-first, traceable, modular, AI-native architecture
- MVP focus: Phases 1-5 deliver core RAG functionality for hackathon demo
