"""
API module for FastAPI web service layer.

Provides RESTful endpoints for frontend-backend communication.
"""

from .app import app
from .models import ChatRequest, ChatResponse, SessionInfo, ErrorResponse
from .middleware import SessionManager

__all__ = ["app", "ChatRequest", "ChatResponse", "SessionInfo", "ErrorResponse", "SessionManager"]
