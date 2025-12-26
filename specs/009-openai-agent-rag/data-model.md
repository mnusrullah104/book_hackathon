# Data Model: OpenAI Agent with RAG Retrieval Integration

**Feature**: 009-openai-agent-rag
**Date**: 2025-12-25
**Phase**: 1 - Design & Contracts

## Overview

This document defines the data structures, entities, and relationships for the RAG-enabled conversational agent. The model emphasizes simplicity, leveraging existing infrastructure while introducing minimal new abstractions for agent-specific functionality.

## Core Entities

### 1. AgentConfig

Configuration container for agent initialization and behavior.

```python
@dataclass
class AgentConfig:
    """Configuration for RAG agent initialization."""

    openai_api_key: str
    """OpenAI API key for agent model access."""

    model: str = "gpt-4-turbo-preview"
    """OpenAI model identifier (gpt-4-turbo-preview, gpt-3.5-turbo, etc.)."""

    system_prompt: str = field(default_factory=lambda: DEFAULT_SYSTEM_PROMPT)
    """Instructions defining agent behavior and retrieval grounding."""

    temperature: float = 0.7
    """Sampling temperature (0.0-2.0). Lower = more deterministic."""

    max_tokens: int = 1000
    """Maximum tokens in agent response."""

    top_k_retrieval: int = 5
    """Default number of chunks to retrieve per query."""

    retrieval_score_threshold: float = 0.3
    """Minimum similarity score for retrieved chunks (0.0-1.0)."""

    cohere_api_key: Optional[str] = None
    """Cohere API key for embeddings (defaults to env var)."""

    qdrant_url: Optional[str] = None
    """Qdrant instance URL (defaults to env var)."""

    qdrant_api_key: Optional[str] = None
    """Qdrant API key (defaults to env var)."""

    collection_name: str = "web_documents"
    """Target Qdrant collection."""

    verbose: bool = False
    """Enable detailed logging."""
```

**Validation Rules**:
- `temperature` must be in range [0.0, 2.0]
- `max_tokens` must be positive integer <= 4096
- `top_k_retrieval` must be in range [1, 20]
- `retrieval_score_threshold` must be in range [0.0, 1.0]
- API keys must be non-empty strings

**State Transitions**: Immutable configuration; created once during agent initialization.

---

### 2. ConversationMessage

Individual message in conversation history following OpenAI format.

```python
@dataclass
class ConversationMessage:
    """A single message in the conversation history."""

    role: str
    """Message role: 'system', 'user', 'assistant', or 'function'."""

    content: Optional[str] = None
    """Message text content (None for function call requests)."""

    name: Optional[str] = None
    """Function name (only for role='function')."""

    function_call: Optional[dict] = None
    """Function call details (only for assistant function invocations)."""

    def to_dict(self) -> dict:
        """Convert to OpenAI API format."""
        msg = {"role": self.role}
        if self.content is not None:
            msg["content"] = self.content
        if self.name is not None:
            msg["name"] = self.name
        if self.function_call is not None:
            msg["function_call"] = self.function_call
        return msg

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationMessage":
        """Create from OpenAI API response."""
        return cls(
            role=data["role"],
            content=data.get("content"),
            name=data.get("name"),
            function_call=data.get("function_call")
        )
```

**Validation Rules**:
- `role` must be one of: "system", "user", "assistant", "function"
- `content` required unless `function_call` is present
- `name` required when `role="function"`
- `function_call` only valid when `role="assistant"`

**State Transitions**:
1. User input → `ConversationMessage(role="user", content=<query>)`
2. Agent function request → `ConversationMessage(role="assistant", function_call={...})`
3. Function execution → `ConversationMessage(role="function", name="search_docs", content=<json>)`
4. Agent response → `ConversationMessage(role="assistant", content=<answer>)`

---

### 3. ConversationSession

Container for conversation state and history.

```python
@dataclass
class ConversationSession:
    """Maintains state for a multi-turn conversation."""

    session_id: str
    """Unique session identifier (UUID4)."""

    messages: List[ConversationMessage] = field(default_factory=list)
    """Ordered conversation history."""

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    """ISO 8601 timestamp of session creation."""

    turn_count: int = 0
    """Number of user turns (queries) in this session."""

    retrieval_count: int = 0
    """Number of retrieval tool invocations."""

    total_tokens_used: int = 0
    """Approximate token usage across all turns."""

    def add_message(self, message: ConversationMessage):
        """Append message to history."""
        self.messages.append(message)
        if message.role == "user":
            self.turn_count += 1
        elif message.role == "function" and message.name == "search_docs":
            self.retrieval_count += 1

    def get_message_history(self) -> List[dict]:
        """Get conversation history in OpenAI API format."""
        return [msg.to_dict() for msg in self.messages]

    def get_last_assistant_message(self) -> Optional[str]:
        """Get most recent assistant response text."""
        for msg in reversed(self.messages):
            if msg.role == "assistant" and msg.content:
                return msg.content
        return None
```

**Validation Rules**:
- `session_id` must be valid UUID4 string
- First message must have `role="system"`
- Messages must alternate between user and assistant (with function messages inserted as needed)

**State Transitions**:
1. **Created**: Empty session with system prompt
2. **Active**: User messages added, agent processing, retrieval invoked
3. **Completed**: Final assistant response added, awaiting next user input

---

### 4. RetrievalToolResponse

Formatted retrieval results for OpenAI function calling.

```python
@dataclass
class RetrievalToolResponse:
    """Structured retrieval results formatted for agent consumption."""

    results: List[dict] = field(default_factory=list)
    """
    List of retrieved chunks, each containing:
    - text: str (truncated to 500 chars)
    - url: str (source document URL)
    - title: str (document title)
    - score: float (similarity score, 3 decimal places)
    """

    total: int = 0
    """Number of results returned."""

    query: str = ""
    """Original search query."""

    error: Optional[str] = None
    """Error type if retrieval failed."""

    message: Optional[str] = None
    """Human-readable error message."""

    execution_time_seconds: float = 0.0
    """Retrieval operation duration."""

    def to_json(self) -> str:
        """Serialize to JSON string for function message content."""
        import json
        return json.dumps({
            "results": self.results,
            "total": self.total,
            "query": self.query,
            "error": self.error,
            "message": self.message,
            "execution_time": round(self.execution_time_seconds, 2)
        }, indent=2)

    def is_error(self) -> bool:
        """Check if retrieval encountered an error."""
        return self.error is not None
```

**Validation Rules**:
- `total` must equal `len(results)` unless `error` is set
- Each result dict must contain keys: `text`, `url`, `title`, `score`
- `score` must be in range [0.0, 1.0]
- If `error` is set, `results` should be empty

**State Transitions**:
1. **Success**: `error=None`, `results` populated, `total > 0`
2. **Empty Results**: `error=None`, `results=[]`, `total=0`
3. **Error**: `error` set, `message` explains failure, `results=[]`

---

### 5. AgentResponse

Complete agent response with metadata.

```python
@dataclass
class AgentResponse:
    """Agent response to user query with metadata."""

    content: str
    """Agent's text response."""

    session_id: str
    """Associated conversation session."""

    turn_number: int
    """Turn index in conversation (1-indexed)."""

    retrieval_performed: bool
    """Whether retrieval tool was invoked."""

    retrieved_sources: List[str] = field(default_factory=list)
    """URLs of documents used for grounding."""

    tokens_used: int = 0
    """Tokens consumed in this turn (approximate)."""

    execution_time_seconds: float = 0.0
    """Total response generation time."""

    error: Optional[str] = None
    """Error message if response generation failed."""
```

**Validation Rules**:
- `content` non-empty unless `error` is set
- `turn_number` must be positive integer
- `retrieved_sources` should be valid URLs when `retrieval_performed=True`

**State Transitions**: Immutable; created after agent completes response generation.

---

## Relationships

```
AgentConfig
    ↓ initializes
RAGAgent (stateful object)
    ↓ creates/manages
ConversationSession
    ↓ contains
List<ConversationMessage>
    ↓ includes
RetrievalToolResponse (as function message content)
    ↓ references
RetrievedChunk (from retrieve.py, existing entity)

RAGAgent
    ↓ produces
AgentResponse
```

## Data Flow

### Single-Turn Query Flow

```
1. User Query
   ↓
2. Create ConversationMessage(role="user", content=query)
   ↓
3. Add to ConversationSession.messages
   ↓
4. Call OpenAI API with conversation history
   ↓
5. OpenAI decides to invoke retrieval function
   ↓
6. Create ConversationMessage(role="assistant", function_call={...})
   ↓
7. Execute retrieval_tool() → RetrievalToolResponse
   ↓
8. Create ConversationMessage(role="function", content=response.to_json())
   ↓
9. Call OpenAI API again with updated history
   ↓
10. OpenAI generates grounded response
    ↓
11. Create ConversationMessage(role="assistant", content=answer)
    ↓
12. Return AgentResponse with metadata
```

### Multi-Turn Conversation Flow

```
ConversationSession (persistent)
    ↓
Turn 1: User query → retrieval → assistant response
    ↓ (messages appended)
Turn 2: User follow-up → (optional retrieval) → assistant response
    ↓ (messages appended)
Turn N: ...
```

## Reused Entities from Existing System

The following entities from `retrieve.py` are reused without modification:

- **RetrievedChunk**: Detailed retrieval result with full metadata
- **RetrievalResult**: Complete search result set from Qdrant
- **ConfigurationError**: Raised for missing API credentials
- **QdrantConnectionError**: Raised for Qdrant connectivity issues
- **CohereAPIError**: Raised for embedding generation failures

## Schema Evolution Considerations

**Future Extensions**:
1. **Session Persistence**: Add database storage for `ConversationSession` (for web deployment)
2. **User Context**: Add `user_id` to `ConversationSession` for multi-user support
3. **Feedback Loop**: Add `feedback: Optional[bool]` to `AgentResponse` for response quality tracking
4. **Advanced Retrieval**: Add `filters: Optional[dict]` to retrieval tool for metadata-based filtering (e.g., specific modules)
5. **Streaming**: Add `stream: bool` to `AgentConfig` for real-time response streaming

**Backward Compatibility**:
- All dataclasses use optional parameters with defaults for extensibility
- JSON serialization via `to_dict()` methods allows schema versioning
- Existing `retrieve.py` entities remain untouched; only consumed by new wrapper layer

## Validation Summary

All entities include:
- **Type annotations**: Full Python type hints for static analysis
- **Validation rules**: Explicit constraints on field values
- **State transitions**: Clear lifecycle documentation
- **Serialization methods**: JSON conversion for API compatibility
- **Error handling**: Explicit error fields and validation failures
