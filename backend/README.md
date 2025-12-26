
### Prerequisites

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables** (add to `.env`):
   ```bash
   # Required: OpenAI API Key
   OPENAI_API_KEY=your-openai-api-key-here

   # Already configured: Cohere and Qdrant
   COHERE_API_KEY=...
   QDRANT_URL=...
   QDRANT_API_KEY=...
   ```

3. **Verify Qdrant Collection**:
   ```bash
   python check_qdrant.py
   ```
   Should confirm `web_documents` collection exists with ingested content.

### Quick Start (Python API)

```python
import asyncio
from agent import create_agent

async def example():
    # Initialize agent
    agent = create_agent(
        model="gpt-4-turbo-preview",  # or "gpt-3.5-turbo" for faster/cheaper
        verbose=True
    )

    # Single query with retrieval
    response = await agent.chat("Explain ROS 2 fundamentals")
    print(response.content)
    print(f"\nSources: {response.retrieved_sources}")
    print(f"Retrieval performed: {response.retrieval_performed}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Response time: {response.execution_time_seconds:.2f}s")

    # Multi-turn conversation (maintains context)
    response1 = await agent.chat("What is Isaac Sim?")
    response2 = await agent.chat("How do I use it for robotics?")
    # Agent remembers context from response1

    # Check session stats
    session = agent.get_session()
    print(f"Turn count: {session.turn_count}")
    print(f"Retrieval count: {session.retrieval_count}")

    # Start fresh session (reset conversation history)
    agent.start_new_session()

asyncio.run(example())
```

### CLI Testing Interface

The `test_agent.py` script provides three modes for testing:

#### 1. Single Query Mode

```bash
# Basic query
python test_agent.py "What is ROS 2?"

# With custom model
python test_agent.py "Explain Isaac Sim" --model gpt-3.5-turbo

# With verbose logging
python test_agent.py "VLA fundamentals" --verbose

# Custom retrieval settings
python test_agent.py "ROS 2 + Isaac Sim" --top-k 10
```

**Output Format**:
```
================================================================================
[QUERY] What is ROS 2?
[RETRIEVING] Yes
[SOURCES] 5 sources retrieved
  1. https://example.com/ros2-intro
  2. https://example.com/ros2-architecture
  3. https://example.com/ros2-features

[RESPONSE]
ROS 2 (Robot Operating System 2) is the next generation of ROS, designed with...
[detailed response with source citations]

**Sources:**
- [ROS 2 Introduction](https://example.com/ros2-intro)

[METADATA]
- Turn: 1
- Tokens: ~250
- Time: 3.4s
- Retrieval: Yes
================================================================================
```

#### 2. Interactive Mode

```bash
python test_agent.py --interactive
```

**Interactive Commands**:
- `/exit`, `/quit` - Exit interactive mode
- `/new`, `/reset` - Start a new session
- `/session` - Show current session info
- `/help` - Show help message

**Example Session**:
```
[Turn 1] You: What is ROS 2?
[Agent] ROS 2 is the next generation of ROS with improved...
[Sources: 5 retrieved]

[Turn 2] You: How do I use it for humanoid robots?
[Agent] Building on ROS 2's capabilities, you can use it for humanoids by...
[Sources: 4 retrieved]

[Turn 3] You: /session
Session ID: abc-123-def-456
Turn count: 2
Retrieval count: 2
Total tokens: 450
```

#### 3. Test Suite Mode

```bash
python test_agent.py --test-suite
```

Runs 8 predefined test queries covering:
- Single-topic queries (ROS 2, Isaac Sim, VLA, Simulation)
- Cross-module integration queries
- Broad/vague queries
- Out-of-scope queries (edge case handling)

**Output includes**:
- Individual test results with validation
- Summary statistics (success rate, average time)
- Success criteria validation (SC-001, SC-002, SC-005 from spec.md)

### Configuration Options

**Agent Initialization**:
```python
agent = create_agent(
    openai_api_key="...",           # Defaults to OPENAI_API_KEY env var
    model="gpt-4-turbo-preview",    # Model identifier
    cohere_api_key="...",           # For embeddings (defaults to env var)
    qdrant_url="...",               # Vector DB URL (defaults to env var)
    qdrant_api_key="...",           # Vector DB key (defaults to env var)
    collection_name="web_documents", # Qdrant collection
    verbose=True                    # Enable detailed logging
)
```

**Query Parameters**:
```python
response = await agent.chat(
    "Your query here",
    top_k=5,              # Number of chunks to retrieve (1-10)
    score_threshold=0.3   # Minimum similarity score (0.0-1.0)
)
```

### Architecture

**Components**:
- `agent.py` - RAG agent implementation with OpenAI function calling
- `retrieve.py` - Vector search and retrieval (existing, reused)
- `test_agent.py` - CLI testing interface

**Data Flow**:
```
User Query → RAGAgent.chat()
  ↓
OpenAI API (decides if retrieval needed)
  ↓
retrieval_tool() → retrieve.search() → Qdrant + Cohere
  ↓
Retrieved chunks → OpenAI API (generate grounded response)
  ↓
AgentResponse (content + sources + metadata)
```

### Troubleshooting

**Error: `openai.AuthenticationError`**
- Check `OPENAI_API_KEY` in `.env` file
- Verify API key is valid at https://platform.openai.com/api-keys

**Error: `ConfigurationError: OPENAI_API_KEY not provided`**
- Ensure `.env` file exists in `backend/` directory
- Run `python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"`

**Agent doesn't cite sources**
- System prompt enforces citations - may indicate retrieval not invoked
- Try more specific queries related to the 4 topic areas
- Check `response.retrieval_performed` and `response.retrieved_sources`

**Slow response times (>10s)**
- Use `gpt-3.5-turbo` instead of `gpt-4-turbo-preview` (10x faster)
- Reduce `top_k` to 3 instead of 5
- Check network latency: `ping api.openai.com`

**High API costs**
- Use `gpt-3.5-turbo` for development (much cheaper)
- Reduce `max_tokens` in `AgentConfig` if responses are too long
- Monitor usage at https://platform.openai.com/usage

See [quickstart guide](../specs/009-openai-agent-rag/quickstart.md) for detailed setup and troubleshooting.

## FastAPI Web Service Integration

The FastAPI web service provides RESTful endpoints for frontend-backend communication with session management, CORS support, and comprehensive error handling.

### Prerequisites

Add FastAPI dependencies to `requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

Add to `.env` file:

```bash
# CORS Configuration (already in .env.example)
ALLOWED_ORIGINS=*  # Development: allow all origins
# ALLOWED_ORIGINS=https://your-frontend.com,https://www.your-frontend.com  # Production
```

### Starting the Server

```bash
cd backend
python api/run_server.py
```

**Default configuration:**
- Host: 0.0.0.0 (all interfaces)
- Port: 8000
- Workers: 1 (single process)
- Reload: Disabled

**Custom options:**
```bash
# Custom host and port
python api/run_server.py --host 127.0.0.1 --port 9000

# Enable auto-reload for development
python api/run_server.py --reload

# Multiple workers (production)
python api/run_server.py --workers 4

# Set log level
python api/run_server.py --log-level debug
```

### API Endpoints

#### POST /api/chat

Send a query to the RAG agent (single or follow-up in conversation).

**Request:**
```json
{
  "query": "Explain ROS 2 fundamentals",
  "session_id": null,           // null = new session, string = follow-up
  "top_k": 5,                     // Optional: chunks to retrieve (1-10, default: 5)
  "model": "gpt-4-turbo-preview"  // Optional: override default model
}
```

**Response (Success):**
```json
{
  "session_id": "abc-123",
  "content": "ROS 2 is the next generation of...",
  "sources": [
    "https://example.com/ros2-intro",
    "https://example.com/ros2-features"
  ],
  "retrieval_performed": true,
  "tokens_used": 350,
  "execution_time_seconds": 3.2,
  "turn_number": 1,
  "error": null,
  "model_config": "gpt-4-turbo-preview"
}
```

**Response (Error):**
```json
{
  "session_id": "abc-123",
  "content": "I'm having trouble accessing the documentation...",
  "sources": [],
  "retrieval_performed": false,
  "tokens_used": 0,
  "execution_time_seconds": 0.5,
  "turn_number": 1,
  "error": "Qdrant connection timeout",
  "model_config": null
}
```

**Example (curl):**
```bash
# New session
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "session_id": null,
    "top_k": 5
  }'

# Follow-up query
curl -X POST http://localhost:8000/api/chat/abc-123 \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I use it for humanoid robots?"
  }'
```

#### POST /api/session/{session_id}/reset

Reset conversation history for a session (starts fresh while keeping same session_id).

**Request:** No body required

**Response:**
```json
{
  "message": "Session reset successfully",
  "session_id": "def-456"  // New session ID
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/session/abc-123/reset
```

#### GET /api/session/{session_id}

Get session statistics and metadata.

**Response:**
```json
{
  "session_id": "abc-123",
  "turn_count": 5,
  "retrieval_count": 4,
  "total_tokens": 1850,
  "created_at": "2025-12-26T10:30:00.000Z"
}
```

**Example (curl):**
```bash
curl -X GET http://localhost:8000/api/session/abc-123
```

#### GET /health

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "service": "rag-agent-api",
  "timestamp": "2025-12-26T10:30:00.000Z"
}
```

### Interactive Documentation

FastAPI provides interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Session Management

- **In-Memory Storage**: Sessions are stored in memory via `SessionManager`
- **Session Timeout**: 1 hour default (configurable)
- **Automatic Cleanup**: Expired sessions are automatically removed
- **Conversation Context**: Maintains history across turns with automatic pruning for token limits

### CORS Configuration

**Development Mode** (default):
```bash
ALLOWED_ORIGINS=*  # Allow all origins
```

**Production Mode:**
```bash
ALLOWED_ORIGINS=https://your-frontend.com,https://www.your-frontend.com
```

CORS configuration is loaded from `ALLOWED_ORIGINS` environment variable in `.env`.

### Error Handling

The API includes comprehensive error handling:

| Status Code | Error Type | Description |
|-------------|-------------|-------------|
| 400         | ValueError | Invalid input (empty query, invalid session_id) |
| 404         | Not Found   | Session not found |
| 500         | Exception  | Internal server error |

All errors return JSON format with `error` field and optional `request_id` for tracing.

### Troubleshooting

#### CORS Issues

**Symptom:** Frontend can't access API (CORS error in browser console)

**Solutions:**
1. Verify `ALLOWED_ORIGINS` in `.env` matches your frontend URL
2. Check for trailing slashes in URLs
3. For production, ensure HTTPS URLs are used

**Example:**
```bash
# .env file (production)
ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-app.com
```

#### Connection Issues

**Symptom:** API returns 500 errors

**Solutions:**
1. Check backend logs for error details
2. Verify Qdrant and Cohere API keys in `.env`
3. Ensure Qdrant collection `web_documents` exists
4. Verify OpenAI API key is valid at https://platform.openai.com/api-keys

**Check Qdrant:**
```bash
cd backend
python check_qdrant.py
```

#### Session Not Found

**Symptom:** 404 error when using existing session_id

**Causes:**
- Session expired (1 hour timeout)
- Server restarted (in-memory sessions cleared)

**Solutions:**
1. Start new session (set `session_id: null` in request)
2. Implement frontend session refresh logic

### Performance

- **API overhead:** <200ms for response processing (excluding agent time)
- **Agent response:** <5s total (includes retrieval, OpenAI API)
- **Concurrent requests:** Supported via uvicorn workers

### Frontend Integration

**React/Vue/Angular Example:**
```javascript
// New session
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is ROS 2?',
    session_id: null,
    top_k: 5
  })
})

// Follow-up with session_id
const followUp = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'How do I use it?',
    session_id: sessionId  // From previous response
  })
})

// Reset session
await fetch(`/api/session/${sessionId}/reset`, { method: 'POST' })

// Get session info
const sessionInfo = await fetch(`/api/session/${sessionId}`)
```

### See Also

- [Agent Quickstart](../specs/009-openai-agent-rag/quickstart.md) - Agent CLI testing
- [Agent Specification](../specs/009-openai-agent-rag/spec.md) - Full feature requirements
- [API Implementation Plan](../specs/009-openai-agent-rag/plan.md) - Architecture details

---

## License
