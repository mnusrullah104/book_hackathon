"""
Middleware for FastAPI web service layer

Provides session management for agent instances, tracking active conversations
in memory with cleanup for expired sessions.
"""

import logging
import time
from typing import Dict, Optional
from agent import create_agent, RAGAgent
from pydantic import BaseModel


logger = logging.getLogger(__name__)


# =============================================================================
# SESSION MANAGER (Phase 6: T045)
# =============================================================================

class SessionManager:
    """
    Manages active agent sessions (in-memory).

    Tracks RAGAgent instances by session_id, handles creation, retrieval,
    and cleanup of expired sessions.
    """

    sessions: Dict[str, RAGAgent] = {}
    """Active sessions indexed by session_id"""

    session_timeout: int = 3600
    """Session timeout in seconds (1 hour default)"""

    session_timestamps: Dict[str, float] = {}
    """Track last access time for each session"""

    def __init__(self, session_timeout: Optional[int] = None):
        """
        Initialize session manager.

        Args:
            session_timeout: Custom timeout in seconds (default: 3600)
        """
        if session_timeout is not None:
            self.session_timeout = session_timeout

        logger.info(f"SessionManager initialized with timeout: {self.session_timeout}s")

    def get_or_create(self, session_id: Optional[str] = None, **agent_kwargs) -> RAGAgent:
        """
        Get existing session or create new one.

        Args:
            session_id: Existing session ID (None = create new)
            **agent_kwargs: Additional arguments for create_agent()

        Returns:
            RAGAgent instance for the session
        """
        # If session_id provided and exists, return it
        if session_id and session_id in self.sessions:
            self.session_timestamps[session_id] = time.time()
            if agent_kwargs.get("verbose"):
                logger.info(f"Retrieved existing session: {session_id}")
            return self.sessions[session_id]

        # Create new session
        # Note: We use the existing agent's session_id, not creating a new one
        # to maintain continuity with the agent's internal session management
        agent = create_agent(**agent_kwargs)

        # Use the agent's internal session ID
        actual_session_id = agent.get_session().session_id
        self.sessions[actual_session_id] = agent
        self.session_timestamps[actual_session_id] = time.time()

        if agent_kwargs.get("verbose"):
            logger.info(f"Created new session: {actual_session_id}")

        return agent

    def get_session(self, session_id: str) -> Optional[RAGAgent]:
        """
        Get existing session by ID.

        Args:
            session_id: Session identifier

        Returns:
            RAGAgent if found, None otherwise
        """
        return self.sessions.get(session_id)

    def reset(self, session_id: str) -> str:
        """
        Reset conversation history for a session.

        Creates a fresh session while reusing the same session ID.

        Args:
            session_id: Session identifier to reset

        Returns:
            New session ID (same as input if session exists)

        Raises:
            ValueError: Session not found
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session not found: {session_id}")

        # Start new session within the same agent instance
        new_session_id = self.sessions[session_id].start_new_session()

        # Update timestamp
        self.session_timestamps[new_session_id] = time.time()

        logger.info(f"Reset session: {session_id} -> {new_session_id}")

        return new_session_id

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from tracking.

        Args:
            session_id: Session identifier to delete

        Returns:
            True if session existed and was deleted, False otherwise
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            del self.session_timestamps[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def cleanup_expired(self) -> int:
        """
        Remove sessions that have exceeded timeout.

        Returns:
            Number of sessions cleaned up
        """
        current_time = time.time()
        expired_sessions = []

        for session_id, last_access in self.session_timestamps.items():
            if current_time - last_access > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self.delete_session(session_id)

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

        return len(expired_sessions)

    def get_active_session_count(self) -> int:
        """
        Get count of currently active sessions.

        Returns:
            Number of active sessions
        """
        return len(self.sessions)

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        Get session metadata for monitoring.

        Args:
            session_id: Session identifier

        Returns:
            Dict with session info or None if not found
        """
        agent = self.sessions.get(session_id)
        if not agent:
            return None

        session = agent.get_session()

        return {
            "session_id": session.session_id,
            "turn_count": session.turn_count,
            "retrieval_count": session.retrieval_count,
            "total_tokens": session.total_tokens_used,
            "created_at": session.created_at,
            "last_access": self.session_timestamps.get(session_id, 0)
        }
