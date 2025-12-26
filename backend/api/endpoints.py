"""
API endpoint definitions for RAG agent

Route definitions separated from app.py for clearer organization.
All routes are registered in api/app.py.
"""

import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from .models import ChatRequest, ChatResponse, SessionInfo, ErrorResponse
from .middleware import SessionManager
from agent import AgentResponse as AgentAgentResponse


logger = logging.getLogger(__name__)


# Session manager instance
session_manager = SessionManager()


async def chat_endpoint_impl(request: ChatRequest, session_mgr: SessionManager) -> ChatResponse:
    """
    Implementation for chat endpoint logic.

    Args:
        request: ChatRequest with query, optional session_id, optional top_k
        session_mgr: SessionManager instance

    Returns:
        ChatResponse with agent response, sources, and metadata

    Raises:
        HTTPException: 400 for invalid input, 500 for processing errors
    """
    import time

    start_time = time.time()

    try:
        # Get or create agent session
        agent = session_mgr.get_or_create(
            session_id=request.session_id,
            verbose=False
        )

        # Call agent chat method
        agent_response: AgentAgentResponse = await agent.chat(
            user_message=request.query,
            top_k=request.top_k if request.top_k else None
        )

        # Convert agent response to API response
        exec_time = time.time() - start_time

        return ChatResponse(
            session_id=agent_response.session_id,
            content=agent_response.content,
            sources=agent_response.retrieved_sources,
            retrieval_performed=agent_response.retrieval_performed,
            tokens_used=agent_response.tokens_used,
            execution_time_seconds=agent_response.execution_time_seconds,
            turn_number=agent_response.turn_number,
            error=agent_response.error,
            model_config=agent.config.model if hasattr(agent, 'config') else None
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


async def get_session_info_impl(session_id: str, session_mgr: SessionManager) -> SessionInfo:
    """
    Implementation for session info endpoint logic.

    Args:
        session_id: Session identifier
        session_mgr: SessionManager instance

    Returns:
        SessionInfo with session metadata

    Raises:
        HTTPException: 404 if session not found
    """
    session_info = session_mgr.get_session_info(session_id)

    if not session_info:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}"
        )

    return SessionInfo(
        session_id=session_info["session_id"],
        turn_count=session_info["turn_count"],
        retrieval_count=session_info["retrieval_count"],
        total_tokens=session_info["total_tokens"],
        created_at=session_info["created_at"]
    )


async def reset_session_impl(session_id: str, session_mgr: SessionManager) -> dict:
    """
    Implementation for session reset endpoint logic.

    Args:
        session_id: Session identifier to reset
        session_mgr: SessionManager instance

    Returns:
        Dict with confirmation message and session_id

    Raises:
        HTTPException: 404 if session not found
    """
    try:
        new_session_id = session_mgr.reset(session_id)
        return {
            "message": "Session reset successfully",
            "session_id": new_session_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
