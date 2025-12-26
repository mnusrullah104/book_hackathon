"""
Type definitions for the RAG agent.

Core data structures for agent, retrieval, and conversation management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class RetrievalResult:
    """Result from vector search operation."""

    chunk_id: str
    """Qdrant point ID."""

    chunk_text: str
    """Content of the retrieved chunk."""

    url: str
    """Source document URL."""

    title: Optional[str]
    """Document title."""

    similarity_score: float
    """Similarity score (0.0-1.0)."""

    chunk_index: int
    """Position in original document."""


@dataclass
class SearchResponse:
    """Complete search response with multiple chunks."""

    query: str
    """Original search query."""

    results: List[RetrievalResult]
    """Retrieved chunks ordered by similarity."""

    total_count: int
    """Number of chunks retrieved."""

    top_score: float
    """Highest similarity score."""

    avg_score: float
    """Average similarity score."""

    execution_time_seconds: float
    """Search duration."""


@dataclass
class AgentResponse:
    """Response from the RAG agent."""

    content: str
    """Agent's text response."""

    sources: List[str]
    """List of source URLs used."""

    retrieval_performed: bool
    """Whether retrieval was invoked."""

    tokens_used: int
    """Approximate token count."""

    execution_time_seconds: float
    """Total response time."""

    error: Optional[str] = None
    """Error message if any."""

    turn_number: int = 1
    """Turn in conversation."""

    session_id: Optional[str] = None
    """Session identifier."""


@dataclass
class ConversationState:
    """State of a multi-turn conversation."""

    session_id: str
    """Unique session identifier."""

    turn_count: int = 0
    """Number of user turns."""

    retrieval_count: int = 0
    """Number of retrievals performed."""

    total_tokens: int = 0
    """Total tokens consumed."""

    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    """Session creation timestamp."""

    messages: List[Dict[str, Any]] = field(default_factory=list)
    """Conversation history (for inspection)."""


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class RetrievalError(AgentError):
    """Retrieval operation failed."""
    pass


class ConfigurationError(AgentError):
    """Configuration error."""
    pass
