# Implementation Plan: FastAPI Integration for RAG Agent

**Branch**: `009-openai-agent-rag` | **Date**: 2025-12-26 | **Spec**: N/A (extension)
**Input**: User requirements for FastAPI web service layer

## Summary

Add FastAPI web service layer to enable frontend-backend communication for the RAG agent. Create RESTful endpoints for single-query and multi-turn conversation interactions, configure CORS for local frontend access, and ensure seamless integration with the existing agent implementation.

## Technical Context

**Language/Version**: Python 3.13 (existing backend environment)
**Primary Dependencies**: FastAPI, Uvicorn, existing RAG agent modules
**Storage**: Uses existing Qdrant + Cohere infrastructure (no new storage)
**Testing**: pytest, FastAPI TestClient, curl/postman for endpoint validation
**Target Platform**: Local development with CORS-enabled frontend access
**Project Type**: Web service extension to existing backend
**Performance Goals**: <200ms API response overhead, support concurrent requests, maintain <5s total response time
**Constraints**: Must preserve existing agent behavior, maintain backward compatibility with CLI testing
**Scale/Scope**: Single FastAPI app with 3-4 core endpoints, RESTful design, production-ready error handling

## Constitution Check

*GATE: Must pass before implementation*

**✅ Spec-first development**: Following established patterns from existing RAG agent spec, web service design aligns with FR-013 (modular design for web integration)

**✅ Technical accuracy and reproducibility**: Using proven FastAPI patterns, clear API contracts with Pydantic models, documented endpoints for reproducibility

**✅ Clarity for developers and AI engineers**: RESTful API design follows best practices, clear request/response models, documented endpoint contracts

**✅ AI-native architecture**: Extends existing RAG agent with web interface, preserves retrieval grounding and multi-turn capabilities

**✅ End-to-end transparency**: API logging at all levels, error propagation with detailed messages, observable request/response flows

**✅ Modular, non-filler content**: Separate API layer from agent logic, focused endpoints without unnecessary abstractions

**GATE STATUS**: ✅ PASS - All constitutional principles satisfied

## Project Structure

### New Files

```text
backend/
├── api/                     # NEW: FastAPI web service layer
│   ├── __init__.py
│   ├── app.py              # FastAPI application instance
│   ├── endpoints.py        # Route definitions
│   ├── models.py           # Pydantic request/response models
│   └── middleware.py       # CORS, error handling, logging
├── config.py               # EXISTING: Configuration management
├── agent.py                # EXISTING: RAG agent (refactored as service)
├── tools/                  # EXISTING: Retrieval tools
└── main.py                 # MODIFIED: Will be api/app.py or moved
```

**Structure Decision**: Create dedicated `api/` module for web service layer, separating concerns between agent logic (service) and API surface (presentation). FastAPI app in `api/app.py`, routes in `api/endpoints.py`, models in `api/models.py`. Existing `agent.py` becomes a service that can be imported by both CLI and API layers.

## Complexity Tracking

No constitutional violations. All decisions align with existing architecture patterns.

---

## Phase 1: Research & Design Decisions

### 1. FastAPI vs Alternative Frameworks

**Decision**: Use FastAPI for web service layer

**Rationale**:
- Built-in Pydantic validation for request/response models
- Automatic OpenAPI/Swagger documentation
- Async support for concurrent agent queries
- Excellent Python type hints integration
- Minimal boilerplate code

**Alternatives Considered**:
1. **Flask**: Less built-in validation, more boilerplate, sync-only (unless using extensions)
2. **Django**: Overkill for single-purpose API, larger footprint
3. **FastAPI**: Best fit for async Python with strong typing

### 2. API Architecture Pattern

**Decision**: RESTful API with session-based conversations

**Rationale**:
- Simple, stateless server design
- Session state managed via session ID returned to client
- Client maintains conversation state (stores session ID)
- Enables frontend to manage conversation UI

**API Pattern**:
```text
POST /api/chat           # Single query (creates new session)
POST /api/chat/{id}      # Follow-up query in conversation
GET  /api/session/{id}    # Get session state
POST /api/session/{id}/reset # Reset conversation
```

### 3. CORS Configuration

**Decision**: Allow all origins for local development, restrict in production

**Rationale**:
- Local frontend development requires CORS
- Use environment-based configuration
- Default: allow all origins (development mode)
- Production: whitelist specific domains

**Implementation**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Session Management

**Decision**: Stateless server with session ID tracking

**Rationale**:
- No session storage on server (except in-memory agent state)
- Client stores session ID in frontend state
- Agent maintains conversation state in memory (non-persistent)
- Enables horizontal scaling (future: Redis session store)

**Session Flow**:
1. First query → server creates new agent session → returns session_id
2. Follow-up queries → client sends session_id → server routes to agent instance
3. Session expiration after timeout or explicit reset

---

## Phase 2: Data Model

### API Request/Response Models

**ChatRequest** (POST /api/chat):
```python
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None  # None = new session
    top_k: Optional[int] = None
```

**ChatResponse**:
```python
class ChatResponse(BaseModel):
    session_id: str
    content: str
    sources: List[str]
    retrieval_performed: bool
    tokens_used: int
    execution_time_seconds: float
    turn_number: int
    error: Optional[str] = None
```

**SessionInfo** (GET /api/session/{id}):
```python
class SessionInfo(BaseModel):
    session_id: str
    turn_count: int
    retrieval_count: int
    total_tokens: int
    created_at: str
```

### Agent Session Storage

```python
class SessionManager:
    """Manages active agent sessions (in-memory)."""

    sessions: Dict[str, RAGAgent] = {}
    session_timeout: int = 3600  # 1 hour

    def get_or_create(session_id: Optional[str]) -> RAGAgent
    def reset(session_id: str) -> str
    def cleanup_expired()
```

---

## Phase 3: API Contracts

### Endpoint 1: POST /api/chat

Create endpoint to accept user query → call Agent → return grounded response

**Request**:
```json
{
  "query": "Explain ROS 2 fundamentals",
  "session_id": null,
  "top_k": 5
}
```

**Response (Success)**:
```json
{
  "session_id": "abc-123",
  "content": "ROS 2 is the next generation...",
  "sources": [
    "https://docs.example.com/ros2-intro",
    "https://docs.example.com/ros2-features"
  ],
  "retrieval_performed": true,
  "tokens_used": 350,
  "execution_time_seconds": 3.2,
  "turn_number": 1,
  "error": null
}
```

**Response (Error)**:
```json
{
  "session_id": "abc-123",
  "content": "I'm having trouble accessing the documentation...",
  "sources": [],
  "retrieval_performed": false,
  "tokens_used": 0,
  "execution_time_seconds": 0.5,
  "turn_number": 1,
  "error": "Qdrant connection timeout"
}
```

### Endpoint 2: POST /api/chat/{session_id}

Follow-up query in existing conversation.

**Request**:
```json
{
  "query": "How do I use it with Isaac Sim?",
  "top_k": 3
}
```

**Response**: Same format as above

### Endpoint 3: GET /api/session/{session_id}

Get session state information.

**Response**:
```json
{
  "session_id": "abc-123",
  "turn_count": 5,
  "retrieval_count": 4,
  "total_tokens": 1800,
  "created_at": "2025-12-26T10:30:00Z"
}
```

### Endpoint 4: POST /api/session/{session_id}/reset

Reset conversation history (starts fresh).

**Response**:
```json
{
  "message": "Session reset successfully",
  "session_id": "abc-123"
}
```

---

## Phase 4: Implementation Strategy

### Order of Implementation

1. **Create API module structure** - Setup directories and __init__.py files
2. **Define Pydantic models** - api/models.py with request/response schemas
3. **Implement SessionManager** - api/middleware.py with session tracking
4. **Create FastAPI app** - api/app.py with CORS and global middleware
5. **Implement endpoints** - api/endpoints.py with 4 core routes
6. **Add error handling** - Global exception handlers and logging
7. **Update entry point** - Modify or create startup script
8. **Test endpoints** - Verify with curl/Postman

### Key Implementation Details

**SessionManager**: In-memory dictionary tracking active sessions
```python
sessions: Dict[str, RAGAgent] = {}

# Create new session
if session_id not in sessions:
    sessions[session_id] = create_agent(config)

# Get session
return sessions[session_id]
```

**Error Handling**:
```python
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

**Logging Middleware**:
```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response
```

---

## Phase 5: Testing Strategy

### API Testing

**1. Unit Tests (pytest + FastAPI TestClient)**:
- Test endpoint with valid requests
- Test error cases (invalid input, missing fields)
- Test session management
- Test CORS headers

**2. Integration Tests (Test Agent via API)**:
- Single query end-to-end
- Multi-turn conversation via API
- Session reset functionality
- Error propagation from agent to API

**3. Manual Testing**:
```bash
# Start server
uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000

# Test endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROS 2?"}'

# Test multi-turn
curl -X POST http://localhost:8000/api/chat/abc-123 \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I use it?"}'
```

### Frontend Integration Test

**Full flow validation**:
1. Frontend sends query to FastAPI
2. FastAPI processes and calls agent
3. Agent performs retrieval
4. Response returned to frontend
5. Frontend displays grounded response with sources

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Research)**: No dependencies
- **Phase 2 (Data Model)**: Depends on existing agent types
- **Phase 3 (API Contracts)**: Depends on Phase 2
- **Phase 4 (Implementation)**: Depends on Phase 2-3
- **Phase 5 (Testing)**: Depends on Phase 4

### Within Phase 4 (Implementation)

1. Create module structure
2. Define Pydantic models (api/models.py)
3. Implement SessionManager (api/middleware.py)
4. Create FastAPI app (api/app.py)
5. Implement endpoints (api/endpoints.py) - depends on 1-4
6. Add error handling - depends on 1-5
7. Update entry point - depends on 1-6

---

## Implementation Strategy

### Incremental Delivery

**Step 1**: Create FastAPI app with single `/health` endpoint
**Step 2**: Add `/api/chat` endpoint (single query only)
**Step 3**: Implement session management and multi-turn `/api/chat/{id}`
**Step 4**: Add session management endpoints
**Step 5**: Test full flow with frontend

Each step validates independently and builds toward full functionality.

---

## Notes

- **FastAPI**: Use async endpoints for concurrent request handling
- **CORS**: Enable for local development, configure for production
- **Session State**: In-memory (no persistence), future: Redis
- **Error Handling**: Preserve agent errors, add API-layer errors
- **Logging**: Request/response logging for debugging
- **Testing**: Use TestClient for unit tests, curl/postman for manual validation
