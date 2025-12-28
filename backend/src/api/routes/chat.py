"""
Chat API Route - RAG-powered conversation endpoint

Provides authenticated chat functionality using the RAG agent
for retrieval-augmented generation responses.
"""

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid
import asyncio
import logging
import sys
import os

# Add backend root to path for agent import
# chat.py -> routes -> api -> src -> backend
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, backend_root)

from ...models.database import get_db
from ...services.auth import verify_session
from ...api.middleware.logging import structured_logger
from slowapi import Limiter
from slowapi.util import get_remote_address

# Import RAG agent
try:
    from agent import create_agent, RAGAgent
    AGENT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"RAG agent not available: {e}")
    AGENT_AVAILABLE = False

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Global agent instance (singleton pattern for efficiency)
_agent_instance: Optional['RAGAgent'] = None


def get_agent() -> Optional['RAGAgent']:
    """Get or create the RAG agent singleton."""
    global _agent_instance

    if not AGENT_AVAILABLE:
        return None

    if _agent_instance is None:
        try:
            _agent_instance = create_agent(verbose=False)
            logging.info("RAG agent initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize RAG agent: {e}")
            return None

    return _agent_instance


class ChatMessageRequest(BaseModel):
    """Request body for chat message."""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")


class ChatMessageResponse(BaseModel):
    """Response body for chat message."""
    response: str = Field(..., description="AI assistant response")
    sources: List[str] = Field(default_factory=list, description="Source URLs used for response")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    response_message_id: str = Field(..., description="Unique message ID")


class ChatErrorResponse(BaseModel):
    """Error response for chat failures."""
    error: str
    message: str
    timestamp: str


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    responses={
        401: {"description": "Not authenticated"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Chat service unavailable"}
    }
)
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    chat_request: ChatMessageRequest,
    db: Session = next(get_db())
):
    """
    Send a message and receive RAG-powered response.

    Requires valid session cookie. Rate limited to 30 requests/minute.
    Uses retrieval-augmented generation to ground responses in documentation.
    """
    timestamp = datetime.utcnow().isoformat() + "Z"
    message_id = str(uuid.uuid4())

    try:
        # Extract and verify session
        session_token = request.cookies.get("session_token")

        if not session_token:
            structured_logger.log_auth_event(
                "chat_unauthorized",
                reason="no_session_token"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated. Please sign in."
            )

        user = verify_session(db, session_token)

        if not user:
            structured_logger.log_auth_event(
                "chat_unauthorized",
                reason="invalid_session"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired. Please sign in again."
            )

        # Log chat request
        structured_logger.log_auth_event(
            "chat_message_received",
            user_id=user.id,
            message_length=len(chat_request.message)
        )

        # Get RAG agent
        agent = get_agent()

        if agent is None:
            structured_logger.log_error(
                "chat_service_unavailable",
                user_id=user.id,
                error="RAG agent not initialized"
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chat service is temporarily unavailable. Please try again later."
            )

        # Process message with RAG agent
        try:
            # Run async chat method
            response = await agent.chat(chat_request.message)

            # Extract response content and sources
            response_text = response.content
            sources = response.retrieved_sources if response.retrieval_performed else []

            structured_logger.log_auth_event(
                "chat_message_success",
                user_id=user.id,
                retrieval_performed=response.retrieval_performed,
                sources_count=len(sources),
                tokens_used=response.tokens_used
            )

            return ChatMessageResponse(
                response=response_text,
                sources=sources,
                timestamp=timestamp,
                response_message_id=message_id
            )

        except Exception as e:
            structured_logger.log_error(
                "chat_agent_error",
                user_id=user.id,
                error=str(e)
            )

            # Return graceful error response
            return ChatMessageResponse(
                response="I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
                sources=[],
                timestamp=timestamp,
                response_message_id=message_id
            )

    except HTTPException:
        raise
    except Exception as e:
        structured_logger.log_error(
            "chat_unexpected_error",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again."
        )


@router.get("/status")
async def chat_status():
    """Check chat service availability."""
    agent = get_agent()

    return {
        "status": "available" if agent else "unavailable",
        "agent_initialized": agent is not None,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
