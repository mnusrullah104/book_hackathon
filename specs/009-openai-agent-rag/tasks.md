---
description: "Task list for OpenAI Agent with RAG Retrieval Integration"
---

# Tasks: OpenAI Agent with RAG Retrieval Integration

**Input**: Design documents from `/specs/009-openai-agent-rag/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are OPTIONAL for this feature. No explicit test requirement found in spec.md. Focus on CLI-based validation per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` for Python agent code
- **API layer**: `backend/api/` for FastAPI web service
- Existing infrastructure: `backend/retrieve.py`, `backend/main.py`, `backend/requirements.txt`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency configuration

- [X] T001 Add openai package to backend/requirements.txt
- [X] T002 [P] Add OPENAI_API_KEY to backend/.env.example with documentation
- [X] T003 [P] Update backend/README.md with agent usage section placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core agent infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create backend/agent.py with AgentConfig dataclass per data-model.md
- [X] T005 [P] Create ConversationMessage dataclass in backend/agent.py with to_dict/from_dict methods
- [X] T006 [P] Create ConversationSession dataclass in backend/agent.py with message history management
- [X] T007 [P] Create RetrievalToolResponse dataclass in backend/agent.py with JSON serialization
- [X] T008 [P] Create AgentResponse dataclass in backend/agent.py with metadata fields
- [X] T009 Implement retrieval_tool() function in backend/agent.py that wraps retrieve.search()
- [X] T010 Add OpenAI function calling schema loading from contracts/retrieval-tool-schema.json
- [X] T011 Load system prompt from contracts/system-prompt.md into AgentConfig
- [X] T012 Implement create_agent() initialization function in backend/agent.py
- [X] T013 Add configuration validation and error handling for missing API keys

**Checkpoint**: Foundation ready - RAGAgent class can now be implemented for user stories

---

## Phase 3: User Story 1 - Basic Query-Response with Retrieval (Priority: P1) 🎯 MVP

**Goal**: Enable an AI engineer to send a natural language query to the agent, which searches stored documentation and returns a grounded response based on relevant content found in the knowledge base.

**Independent Test**: Send query "Explain Isaac Sim fundamentals" → Agent retrieves top 5 chunks from Module 3 → Response includes citations with source URLs

### Implementation for User Story 1

- [X] T014 [US1] Implement RAGAgent class initialization in backend/agent.py with session creation
- [X] T015 [US1] Implement RAGAgent._call_openai() method for Chat Completions API interaction
- [X] T016 [US1] Implement function call detection and retrieval_tool invocation logic in RAGAgent
- [X] T017 [US1] Implement retrieval result injection as function message in conversation history
- [X] T018 [US1] Implement RAGAgent.chat() method orchestrating: query → OpenAI → function call → retrieval → response
- [X] T019 [US1] Add error handling for QdrantConnectionError and CohereAPIError in chat()
- [X] T020 [US1] Add error handling for OpenAI API errors (rate limits, authentication, invalid requests)
- [X] T021 [US1] Implement graceful degradation when retrieval returns empty results
- [X] T022 [US1] Add token usage tracking and response metadata collection in AgentResponse
- [X] T023 [US1] Implement source URL extraction from retrieval results for AgentResponse.retrieved_sources

**Checkpoint**: At this point, User Story 1 should be fully functional - single-turn query/response with retrieval grounding

---

## Phase 4: User Story 2 - Multi-Turn Conversation with Context Retention (Priority: P2)

**Goal**: Enable an AI engineer to engage in a multi-turn conversation where the agent maintains context across multiple queries and performs retrieval as needed for each turn.

**Independent Test**: Start conversation with "What is ROS 2?" then follow up with "How do I use it for humanoid robots?" → Agent understands context without repeating background

### Implementation for User Story 2

- [X] T024 [US2] Implement ConversationSession.get_message_history() for OpenAI message format
- [X] T025 [US2] Update RAGAgent.chat() to append user messages to existing conversation history
- [X] T026 [US2] Update RAGAgent.chat() to pass full conversation history to OpenAI API
- [X] T027 [US2] Implement conversation context pruning for token limit management (if history exceeds threshold)
- [X] T028 [US2] Add turn_count and retrieval_count tracking in ConversationSession
- [X] T029 [US2] Implement RAGAgent.get_session() method returning current ConversationSession state
- [ ] T030 [US2] Test multi-turn conversation with 5+ turns maintaining coherent context

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - multi-turn conversations with context retention

---

## Phase 5: User Story 3 - Local Testing and Validation (Priority: P1)

**Goal**: Enable an AI engineer to test the agent locally in a terminal or notebook environment to validate retrieval quality and response accuracy before integration with external systems.

**Independent Test**: Run test script with 10 sample queries → All queries process successfully → Results printed in readable format with retrieval status

### Implementation for User Story 3

- [X] T031 [P] [US3] Create backend/test_agent.py CLI script with argparse setup
- [X] T032 [P] [US3] Implement single query mode in test_agent.py: parse query from CLI args
- [X] T033 [US3] Implement test_agent.py output formatting: query, retrieval status, sources, response, metadata
- [X] T034 [US3] Implement interactive mode in test_agent.py with REPL loop for multi-turn testing
- [X] T035 [US3] Implement RAGAgent.start_new_session() method for resetting conversation history
- [X] T036 [US3] Add --model, --top-k, --verbose CLI arguments to test_agent.py
- [X] T037 [US3] Implement test suite mode in test_agent.py with predefined queries from quickstart.md
- [X] T038 [US3] Add test queries spanning all 4 modules (ROS 2, Simulation, Isaac, VLA) to test suite
- [X] T039 [US3] Add out-of-scope test query ("What's the weather today?") for edge case validation
- [X] T040 [US3] Implement test result validation: check retrieval performed, sources cited, graceful failures
- [X] T041 [US3] Add summary statistics output: success rate, average response time, retrieval percentage

**Checkpoint**: All user stories should now be independently functional - complete CLI testing interface operational

---

## Phase 6: User Story 4 - FastAPI Web Service Integration (Priority: P2) 🌐

**Goal**: Add FastAPI web service layer to enable frontend-backend communication for the RAG agent. Create RESTful endpoints for single-query and multi-turn conversation interactions with CORS-enabled local frontend access.

**Independent Test**: Start FastAPI server → Send POST request to /api/chat → Receive grounded JSON response with session_id and sources → Verify CORS headers allow frontend access

### API Module Setup

- [X] T042 [P] [US4] Create backend/api/ directory structure with __init__.py
- [X] T043 [P] [US4] Add fastapi and uvicorn to backend/requirements.txt
- [X] T044 [US4] Create backend/api/models.py with Pydantic request/response models per plan.md Phase 2
  - [ ] ChatRequest with query, session_id, top_k fields
  - [ ] ChatResponse with session_id, content, sources, tokens, execution_time, turn_number, error
  - [ ] SessionInfo with session_id, turn_count, retrieval_count, total_tokens, created_at

### Session Management

- [X] T045 [US4] Implement SessionManager class in backend/api/middleware.py with in-memory session storage
  - [X] Add sessions: Dict[str, RAGAgent] for tracking active sessions
  - [X] Implement get_or_create(session_id: Optional[str]) -> RAGAgent method
  - [X] Implement reset(session_id: str) -> str method for session cleanup
  - [X] Implement cleanup_expired() method for session timeout management

### FastAPI Application Setup

- [X] T046 [US4] Create FastAPI app in backend/api/app.py with configuration
  - [X] Import FastAPI and configure app instance
  - [X] Add CORS middleware with ALLOWED_ORIGINS from environment variable
  - [X] Configure request logging middleware for debugging
  - [X] Initialize SessionManager for session tracking

### Error Handling Middleware

- [X] T047 [US4] Implement global exception handlers in backend/api/app.py
  - [X] Add ValueError handler for invalid input (400 status)
  - [X] Add general exception handler for internal errors (500 status)
  - [X] Ensure errors propagate to ChatResponse.error field
  - [X] Add request/response logging for debugging

### Core API Endpoints

- [X] T048 [US4] Implement POST /api/chat endpoint for single and follow-up queries in backend/api/app.py
  - [X] Accept ChatRequest with optional session_id (None = new session)
  - [X] Get or create agent session via SessionManager
  - [X] Call agent.chat() with query and parameters
  - [X] Return ChatResponse with session metadata
  - [X] Handle retrieval and API errors gracefully

- [X] T049 [US4] Implement GET /api/session/{session_id} endpoint for session state in backend/api/app.py
  - [X] Retrieve agent session from SessionManager
  - [X] Return SessionInfo with turn count, retrieval count, tokens
  - [X] Return 404 if session not found

- [X] T050 [US4] Implement POST /api/session/{session_id}/reset endpoint in backend/api/app.py
  - [X] Call agent.start_new_session() for specified session
  - [X] Return confirmation message with session_id
  - [X] Return 404 if session not found

### Entry Point and Deployment

- [X] T051 [US4] Create backend/api/run_server.py script to start FastAPI server
  - [X] Import app from backend/api/app.py
  - [X] Use uvicorn.run() with host 0.0.0.0, port 8000, reload=True
  - [X] Add command-line argument parsing for custom host/port
  - [X] Include server startup logging

- [X] T052 [US4] Add ALLOWED_ORIGINS environment variable to backend/.env.example
  - [X] Document CORS configuration for local development
  - [X] Provide example for production domain whitelist

### API Documentation and Testing

- [X] T053 [P] [US4] Update backend/README.md with FastAPI integration section
  - [X] Document all API endpoints with request/response examples
  - [X] Include curl command examples for testing
  - [X] Document environment variable setup (ALLOWED_ORIGINS)
  - [X] Add troubleshooting section for CORS and connection issues

- [ ] T054 [US4] Test FastAPI endpoints using curl or Postman (requires OPENAI_API_KEY)
  - [ ] Test POST /api/chat with new session (session_id=null)
  - [ ] Test POST /api/chat/{id} with follow-up query
  - [ ] Test GET /api/session/{id} for session info
  - [ ] Test POST /api/session/{id}/reset for session reset
  - [ ] Verify CORS headers allow frontend access

**Checkpoint**: FastAPI web service operational - agent accessible via REST API with frontend integration ready

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final integration checks

- [X] T055 [P] Update backend/README.md with complete agent usage documentation
- [X] T056 [P] Add agent.py code examples to backend/README.md (single query, multi-turn, test suite)
- [X] T057 [P] Document environment variable setup in backend/README.md (OPENAI_API_KEY)
- [X] T058 [P] Add troubleshooting section to backend/README.md referencing quickstart.md
- [ ] T059 Validate agent behavior against quickstart.md validation checklist (requires OPENAI_API_KEY)
- [ ] T060 Run test_agent.py --test-suite and verify 90%+ success rate per success criteria SC-001 (requires OPENAI_API_KEY)
- [ ] T061 Measure average response time and verify <5s per query per success criteria SC-005 (requires OPENAI_API_KEY)
- [ ] T062 Verify source citations appear in all domain-related responses per success criteria SC-002 (requires OPENAI_API_KEY)
- [ ] T063 Test edge cases: empty results, connection failures, out-of-scope queries per success criteria SC-007 (requires OPENAI_API_KEY)
- [X] T064 [P] Add docstrings to all public functions in agent.py following Google style
- [X] T065 [P] Add type hints to all function signatures in agent.py
- [X] T066 Run python -m py_compile backend/agent.py to check syntax
- [X] T067 Run python -m py_compile backend/test_agent.py to check syntax
- [X] T068 Validate contracts/retrieval-tool-schema.json matches implemented function signature
- [X] T069 Validate system prompt in agent.py matches contracts/system-prompt.md
- [ ] T070 Add OpenAPI documentation for FastAPI endpoints at /docs endpoint
- [ ] T071 Test frontend-backend integration with CORS-enabled local development

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5, 6)**: All depend on Foundational phase completion
  - User Story 1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - User Story 2 (Phase 4): Depends on User Story 1 completion (builds on chat() method)
  - User Story 3 (Phase 5): Can start after Foundational - Independent but benefits from US1/US2 being complete for testing
  - User Story 4 (Phase 6): Depends on User Stories 1-3 being functional (needs working agent to expose via API)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Implements core chat functionality
- **User Story 2 (P2)**: Depends on User Story 1 - Extends chat() with conversation history
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Independent CLI testing interface
- **User Story 4 (P2)**: Depends on User Stories 1-3 - Requires functional agent to expose via web API

### Within Each User Story

- **User Story 1**: T014 (RAGAgent class) before T015-T023 (methods)
- **User Story 2**: All tasks modify existing RAGAgent.chat() from US1
- **User Story 3**: All CLI tasks can run in parallel with [P] marker
- **User Story 4**:
  - T042-T044 (module setup) can run in parallel
  - T045 (SessionManager) before T046 (app initialization)
  - T046 (app setup) before T047-T050 (endpoints)
  - T047-T050 (endpoints) can run in parallel
  - T051-T052 (entry point, env vars) after endpoints
  - T053-T054 (docs, testing) after implementation

### Parallel Opportunities

- **Phase 1 (Setup)**: T002 and T003 can run in parallel (different files)
- **Phase 2 (Foundational)**: T005, T006, T007, T008 (dataclasses) can all run in parallel
- **Phase 3 (User Story 1)**: Tasks must be sequential (building RAGAgent class methods)
- **Phase 5 (User Story 3)**: T031, T032 can start in parallel
- **Phase 6 (User Story 4)**: T042, T043, T044 can run in parallel; T048-T050 can run in parallel
- **Phase 7 (Polish)**: T055, T056, T057, T058, T064, T065 (documentation) can all run in parallel

---

## Parallel Example: Setup Phase

```bash
# Launch Setup tasks together:
Task: "Add OPENAI_API_KEY to backend/.env.example with documentation"
Task: "Update backend/README.md with agent usage section placeholder"
```

## Parallel Example: Foundational Phase

```bash
# Launch all dataclass creation tasks together:
Task: "Create ConversationMessage dataclass in backend/agent.py"
Task: "Create ConversationSession dataclass in backend/agent.py"
Task: "Create RetrievalToolResponse dataclass in backend/agent.py"
Task: "Create AgentResponse dataclass in backend/agent.py"
```

## Parallel Example: User Story 3

```bash
# Launch CLI implementation tasks together:
Task: "Create backend/test_agent.py CLI script with argparse setup"
Task: "Implement single query mode in test_agent.py"
```

## Parallel Example: User Story 4 (FastAPI)

```bash
# Launch API module setup together:
Task: "Create backend/api/ directory structure with __init__.py"
Task: "Add fastapi and uvicorn to backend/requirements.txt"
Task: "Create backend/api/models.py with Pydantic request/response models"

# Launch endpoint implementations together:
Task: "Implement POST /api/chat endpoint for single and follow-up queries"
Task: "Implement GET /api/session/{session_id} endpoint for session state"
Task: "Implement POST /api/session/{session_id}/reset endpoint"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (core chat with retrieval)
4. Complete Phase 5: User Story 3 (CLI testing interface)
5. **STOP and VALIDATE**: Test User Story 1 with test_agent.py
6. Success criteria: Single query returns grounded response with sources

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test with CLI → MVP functional! ✅
3. Add User Story 3 (CLI) → Enhanced testing capability → Validate US1
4. Add User Story 2 → Multi-turn conversations → Full CLI feature complete
5. Add User Story 4 (FastAPI) → Web service layer → Frontend integration ready
6. Polish Phase → Production-ready documentation and validation

### Recommended Execution Order

**Sprint 1 (MVP)**:
- Phase 1: Setup (T001-T003)
- Phase 2: Foundational (T004-T013)
- Phase 3: User Story 1 (T014-T023)

**Sprint 2 (Testing & Multi-turn)**:
- Phase 5: User Story 3 (T031-T041) - CLI testing
- Phase 4: User Story 2 (T024-T030) - Multi-turn conversations

**Sprint 3 (Web Service)**:
- Phase 6: User Story 4 (T042-T054) - FastAPI integration

**Sprint 4 (Polish)**:
- Phase 7: Documentation and validation (T055-T071)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- US1 (core chat) is prerequisite for US2 (multi-turn) but US3 (CLI) is independent
- US4 (FastAPI) depends on US1-3 being functional
- Focus on single file (agent.py) for CLI tasks simplifies parallelization - most tasks sequential
- test_agent.py tasks are highly parallelizable
- FastAPI tasks in backend/api/ are parallelizable across different files
- Commit after each task or logical group
- Stop after Phase 3 to validate MVP with manual CLI testing
- Avoid: adding features beyond spec, complex abstractions, premature optimization

---

## Success Criteria Validation Map

This maps tasks to success criteria from spec.md:

- **SC-001** (95% query success): Validated by T060 (test suite run)
- **SC-002** (source citations): Validated by T062 (verify citations)
- **SC-003** (5+ turn coherence): Validated by T030 (multi-turn test)
- **SC-004** (<2min test suite): Validated by T060 (test suite timing)
- **SC-005** (<5s response time): Validated by T061 (response time measurement)
- **SC-006** (90% grounding): Manual validation during T059 (quickstart validation)
- **SC-007** (edge case handling): Validated by T063 (edge case testing)
