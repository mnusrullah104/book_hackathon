# Agent API Contract

**Version**: 1.0
**Date**: 2025-12-25
**Purpose**: Define public interfaces for RAG agent interaction

## Public Functions

### 1. `create_agent`

Initialize a new RAG agent instance.

**Signature**:
```python
def create_agent(
    openai_api_key: Optional[str] = None,
    model: str = "gpt-4-turbo-preview",
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
    collection_name: str = "web_documents",
    verbose: bool = False
) -> RAGAgent
```

**Parameters**:
- `openai_api_key`: OpenAI API key (defaults to `OPENAI_API_KEY` env var)
- `model`: OpenAI model identifier (default: "gpt-4-turbo-preview")
- `cohere_api_key`: Cohere API key for embeddings (defaults to env var)
- `qdrant_url`: Qdrant instance URL (defaults to env var)
- `qdrant_api_key`: Qdrant API key (defaults to env var)
- `collection_name`: Target Qdrant collection (default: "web_documents")
- `verbose`: Enable detailed logging (default: False)

**Returns**: Initialized `RAGAgent` instance

**Raises**:
- `ConfigurationError`: Missing required API credentials
- `QdrantConnectionError`: Cannot connect to Qdrant instance
- `ValueError`: Invalid model name or parameters

**Example**:
```python
from agent import create_agent

agent = create_agent(
    model="gpt-4-turbo-preview",
    verbose=True
)
```

---

### 2. `RAGAgent.chat`

Send a message to the agent and get a response.

**Signature**:
```python
async def chat(
    self,
    user_message: str,
    top_k: int = 5,
    score_threshold: float = 0.3
) -> AgentResponse
```

**Parameters**:
- `user_message`: User's natural language query (non-empty string)
- `top_k`: Number of chunks to retrieve (1-10, default: 5)
- `score_threshold`: Minimum similarity score for retrieval (0.0-1.0, default: 0.3)

**Returns**: `AgentResponse` with:
- `content`: Agent's text response
- `session_id`: Conversation session identifier
- `turn_number`: Current turn in conversation
- `retrieval_performed`: Whether retrieval was invoked
- `retrieved_sources`: List of source URLs used
- `tokens_used`: Approximate token consumption
- `execution_time_seconds`: Response generation time
- `error`: Error message (if failed)

**Raises**:
- `ValueError`: Empty or invalid `user_message`
- `CohereAPIError`: Embedding generation failed
- `QdrantConnectionError`: Retrieval search failed
- `openai.error.OpenAIError`: Agent API call failed

**Example**:
```python
response = await agent.chat("Explain ROS 2 fundamentals")
print(response.content)
print(f"Sources: {response.retrieved_sources}")
```

---

### 3. `RAGAgent.start_new_session`

Reset conversation history and start a fresh session.

**Signature**:
```python
def start_new_session(self) -> str
```

**Returns**: New session ID (UUID4 string)

**Example**:
```python
new_session_id = agent.start_new_session()
response = await agent.chat("Hello, what can you help me with?")
```

---

### 4. `RAGAgent.get_session`

Retrieve current conversation session state.

**Signature**:
```python
def get_session(self) -> ConversationSession
```

**Returns**: `ConversationSession` with:
- `session_id`: Session identifier
- `messages`: List of conversation messages
- `created_at`: Session creation timestamp
- `turn_count`: Number of user turns
- `retrieval_count`: Number of retrieval invocations
- `total_tokens_used`: Cumulative token usage

**Example**:
```python
session = agent.get_session()
print(f"Turn count: {session.turn_count}")
print(f"Retrieval count: {session.retrieval_count}")
```

---

### 5. `RAGAgent.get_message_history`

Get conversation history in OpenAI API format.

**Signature**:
```python
def get_message_history(self) -> List[dict]
```

**Returns**: List of message dictionaries with keys:
- `role`: "system" | "user" | "assistant" | "function"
- `content`: Message text (optional)
- `name`: Function name (for function messages)
- `function_call`: Function invocation details (for assistant function calls)

**Example**:
```python
history = agent.get_message_history()
for msg in history:
    print(f"{msg['role']}: {msg.get('content', '[function call]')}")
```

---

## CLI Interface

### `test_agent.py`

Command-line interface for testing agent behavior.

**Usage**:
```bash
# Single query
python test_agent.py "What is ROS 2?"

# Interactive mode
python test_agent.py --interactive

# Run test suite
python test_agent.py --test-suite

# Custom model
python test_agent.py "Explain Isaac Sim" --model gpt-3.5-turbo

# Verbose logging
python test_agent.py "VLA fundamentals" --verbose
```

**Arguments**:
- `query`: Natural language query (positional, optional)
- `--interactive`: Start interactive REPL mode
- `--test-suite`: Run predefined test queries
- `--model`: OpenAI model to use (default: gpt-4-turbo-preview)
- `--top-k`: Number of chunks to retrieve (default: 5)
- `--verbose`: Enable detailed logging
- `--new-session`: Start fresh session (discard history)

**Output Format**:
```
[QUERY] What is ROS 2?
[RETRIEVING] Searching documentation...
[SOURCES] 5 chunks retrieved from 3 documents
[RESPONSE]
ROS 2 (Robot Operating System 2) is...

**Sources:**
- [ROS 2 Basics](https://example.com/module1/ros2)

[METADATA]
- Turn: 1
- Tokens: ~250
- Time: 3.2s
- Retrieval: Yes
```

---

## Error Handling

### Error Response Format

When errors occur, `AgentResponse.error` is populated:

```python
AgentResponse(
    content="",
    session_id="abc-123",
    turn_number=2,
    retrieval_performed=False,
    error="OpenAI API rate limit exceeded",
    execution_time_seconds=0.5
)
```

### Error Types

| Error Type | Cause | Recovery |
|------------|-------|----------|
| `ConfigurationError` | Missing API credentials | Check `.env` file and environment variables |
| `QdrantConnectionError` | Cannot reach Qdrant | Verify Qdrant URL and API key, check network |
| `CohereAPIError` | Embedding generation failed | Check Cohere API key and rate limits |
| `openai.error.RateLimitError` | OpenAI rate limit | Wait and retry, or reduce request frequency |
| `openai.error.InvalidRequestError` | Invalid request format | Check message format and token limits |
| `ValueError` | Invalid parameter values | Validate input parameters |

### Graceful Degradation

When retrieval fails but the agent remains functional:

```python
# Retrieval tool returns error
{
    "error": "Qdrant connection timeout",
    "message": "Unable to search documentation at this time",
    "results": []
}

# Agent acknowledges limitation in response
"I'm having trouble accessing the documentation right now. Please try again in a moment."
```

---

## Rate Limits and Quotas

### OpenAI API Limits

- **Free tier**: 3 RPM (requests per minute), 40k TPM (tokens per minute)
- **Pay-as-you-go**: Varies by model (gpt-4-turbo: 10k TPM, gpt-3.5-turbo: 90k TPM)
- **Retry strategy**: Exponential backoff with 3 max retries

### Cohere API Limits

- **Free tier**: 5 requests/second, 1000 requests/month
- **Production tier**: 10k requests/second
- **Handled by**: `retrieve.py` existing rate limit logic

### Qdrant Limits

- **Free tier**: 1GB storage, unlimited queries
- **Connection pooling**: Single client instance per agent

---

## Versioning

**Current Version**: 1.0 (CLI-only interface)

**Future Versions**:
- **1.1**: Add FastAPI REST endpoints
- **1.2**: WebSocket support for streaming responses
- **1.3**: Batch query processing
- **2.0**: Multi-agent orchestration

**Backward Compatibility**: All public functions maintain signature compatibility within major versions. Deprecation warnings issued one minor version before removal.

---

## Testing Contract

### Unit Test Coverage

Required tests for API compliance:

1. ✅ `test_create_agent_with_valid_config()`
2. ✅ `test_create_agent_missing_credentials_raises_error()`
3. ✅ `test_chat_single_turn_with_retrieval()`
4. ✅ `test_chat_multi_turn_maintains_context()`
5. ✅ `test_chat_empty_message_raises_error()`
6. ✅ `test_retrieval_failure_handled_gracefully()`
7. ✅ `test_start_new_session_resets_history()`
8. ✅ `test_get_session_returns_correct_state()`

### Integration Test Scenarios

1. ✅ End-to-end query with retrieval and response
2. ✅ Multi-turn conversation across 5+ turns
3. ✅ Out-of-scope query handling
4. ✅ Retrieval error recovery
5. ✅ Token limit handling for long conversations
