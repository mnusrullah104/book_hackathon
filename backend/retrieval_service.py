"""
Retrieval service wrapper for RAG agent.

Provides async interface to search functionality with error handling.

This file wraps the retrieval_tool from tools/__init__.py for easier importing.
"""

from tools import search, RetrievalResult


__all__ = ["search", "RetrievalResult"]
