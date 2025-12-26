"""
API Request/Response Models for FastAPI Web Service Layer

Defines Pydantic models for chat requests, responses, and session management.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request for single query or follow-up in conversation."""

    query: str
    """Natural language search query from user"""

    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for multi-turn conversation (None = new session)"
    )

    top_k: Optional[int] = Field(
        default=5,
        description="Number of chunks to retrieve (default: 5, max: 10)",
        ge=1,
        le=10
    )

    model: Optional[str] = Field(
        default=None,
        description="Override default agent model"
    )


class ChatResponse(BaseModel):
    """Response from agent with grounded sources and metadata."""

    session_id: str
    """Session identifier for conversation tracking"""

    content: str
    """Agent's text response"""

    sources: List[str] = Field(
        default_factory=list,
        description="List of source URLs used for grounding"
    )

    retrieval_performed: bool
    """Whether agent performed retrieval for this query"""

    tokens_used: int
    """Approximate token count consumed"""

    execution_time_seconds: float
    """Total response generation time including retrieval"""

    turn_number: int
    """Current turn in conversation"""

    error: Optional[str] = Field(
        default=None,
        description="Error message if request failed"
    )

    model_config: Optional[str] = Field(
        default=None,
        description="Model name used for this response"
    )


class SessionInfo(BaseModel):
    """Information about an active conversation session."""

    session_id: str
    """Session identifier"""

    turn_count: int = Field(
        default=0,
        description="Number of user turns (queries) in this session"
    )

    retrieval_count: int = Field(
        default=0,
        description="Number of retrieval operations performed"
    )

    total_tokens: int = Field(
        default=0,
        description="Cumulative tokens consumed across all turns"
    )

    created_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 timestamp when session was created"
    )


class SessionResetRequest(BaseModel):
    """Request to reset conversation history."""

    confirm: bool = Field(
        default=False,
        description="Must be true to confirm session reset"
    )


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str
    """Error message describing what went wrong"""

    status_code: int = Field(
        default=500,
        description="HTTP status code (400, 401, 500, etc.)"
    )

    request_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for tracing the request"
    )
