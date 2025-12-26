"""
FastAPI application for RAG agent web service

Provides RESTful endpoints for agent interaction with CORS support,
session management, request logging, and global error handling.
"""

import os
import time
import logging
import uuid
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .middleware import SessionManager
from .models import ChatRequest, ChatResponse, SessionInfo, ErrorResponse


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logger = logging.getLogger(__name__)


# =============================================================================
# FASTAPI APPLICATION SETUP (Phase 6: T046-T047)
# =============================================================================

app = FastAPI(
    title="RAG Agent API",
    description="RESTful API for intelligent agent with document retrieval",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Initialize session manager
session_manager = SessionManager()


# =============================================================================
# CORS MIDDLEWARE
# =============================================================================

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.getenv("ALLOWED_ORIGINS"):
    logger.info(f"CORS enabled for origins: {allowed_origins}")
else:
    logger.info("CORS enabled for all origins (development mode)")


# =============================================================================
# REQUEST LOGGING MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests with timing information.

    Args:
        request: FastAPI Request object
        call_next: Next middleware/handler in chain

    Returns:
        Response from next handler
    """
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} "
        f"- {response.status_code} - {duration_ms:.2f}ms"
    )

    return response


# =============================================================================
# GLOBAL EXCEPTION HANDLERS (Phase 6: T047)
# =============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Handle ValueError exceptions (e.g., empty query, invalid session).

    Args:
        request: FastAPI Request object
        exc: ValueError exception

    Returns:
        JSONResponse with 400 status and error message
    """
    logger.warning(f"ValueError: {exc}")
    request_id = str(uuid.uuid4())

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error=str(exc),
            status_code=400,
            request_id=request_id
        ).dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException.

    Args:
        request: FastAPI Request object
        exc: HTTPException

    Returns:
        JSONResponse with appropriate status code and detail
    """
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")
    request_id = str(uuid.uuid4())

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code,
            request_id=request_id
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unexpected exceptions.

    Args:
        request: FastAPI Request object
        exc: Unexpected exception

    Returns:
        JSONResponse with 500 status and generic error message
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    request_id = str(uuid.uuid4())

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            status_code=500,
            request_id=request_id
        ).dict()
    )


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dict with service status
    """
    return {
        "status": "healthy",
        "service": "rag-agent-api",
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# API ENDPOINTS (Phase 6: T048-T050)
# =============================================================================

from agent import AgentResponse as AgentAgentResponse


@app.post("/api/chat", response_model=ChatResponse, status_code=200)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Process user query with the agent (single or follow-up).

    Accepts a new query or follow-up in existing conversation.
    Manages session creation and retrieval automatically.

    Args:
        request: ChatRequest with query, optional session_id, optional top_k

    Returns:
        ChatResponse with agent response, sources, and metadata

    Raises:
        HTTPException: 400 for invalid input, 500 for processing errors
    """
    start_time = time.time()

    try:
        # Get or create agent session
        agent = session_manager.get_or_create(
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


@app.get("/api/session/{session_id}", response_model=SessionInfo, status_code=200)
async def get_session_info(session_id: str) -> SessionInfo:
    """
    Get information about an active conversation session.

    Returns session statistics including turn count, retrieval count,
    total tokens used, and timestamps.

    Args:
        session_id: Session identifier

    Returns:
        SessionInfo with session metadata

    Raises:
        HTTPException: 404 if session not found
    """
    session_info = session_manager.get_session_info(session_id)

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


@app.post("/api/session/{session_id}/reset", status_code=200)
async def reset_session(session_id: str) -> Dict[str, str]:
    """
    Reset conversation history for a session.

    Creates a fresh session while maintaining the same session_id
    for frontend simplicity.

    Args:
        session_id: Session identifier to reset

    Returns:
        Dict with confirmation message and session_id

    Raises:
        HTTPException: 404 if session not found
    """
    try:
        new_session_id = session_manager.reset(session_id)
        return {
            "message": "Session reset successfully",
            "session_id": new_session_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get("/api/sessions", status_code=200)
async def list_sessions() -> Dict[str, int]:
    """
    Get count of active sessions (for monitoring).

    Returns:
        Dict with active session count
    """
    count = session_manager.get_active_session_count()
    return {
        "active_sessions": count
    }


# =============================================================================
# STARTUP LOGGING
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Log application startup.
    """
    logger.info("=" * 60)
    logger.info("RAG Agent API starting up...")
    logger.info(f"FastAPI version: 0.109.0")
    logger.info(f"Session timeout: {session_manager.session_timeout}s")
    logger.info(f"CORS origins: {allowed_origins}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Log application shutdown.
    """
    logger.info("RAG Agent API shutting down...")
    logger.info("Goodbye!")
