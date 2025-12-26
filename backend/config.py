"""
Configuration management for RAG agent.

Centralized configuration with environment variable loading and validation.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv


@dataclass
class AppConfig:
    """Application-wide configuration."""

    # OpenAI Configuration (or OpenRouter)
    openai_api_key: str
    """OpenAI API key for agent and tool operations (or OpenRouter API key)."""

    openai_base_url: Optional[str] = None
    """Custom base URL for OpenAI-compatible API (e.g., 'https://openrouter.ai/api/v1' for OpenRouter)."""

    # Cohere Configuration (for embeddings)
    cohere_api_key: str
    """Cohere API key for embedding generation."""

    # Qdrant Configuration (for vector storage)
    qdrant_url: str
    """Qdrant instance URL."""

    qdrant_api_key: str
    """Qdrant API key for authentication."""

    collection_name: str = "web_documents"
    """Target Qdrant collection for retrieval."""

    # Agent Configuration
    agent_model: str = "mistralai/devstral-2-2512:free"
    """Model identifier for agent (OpenRouter or OpenAI)."""

    agent_temperature: float = 0.7
    """Sampling temperature for agent responses."""

    agent_max_tokens: int = 1000
    """Maximum tokens in agent response."""

    agent_system_prompt: Optional[str] = None
    """Custom system prompt for the agent."""

    # Retrieval Configuration
    top_k_retrieval: int = 5
    """Default number of chunks to retrieve."""

    retrieval_score_threshold: float = 0.3
    """Minimum similarity score for retrieved chunks."""

    # Application Configuration
    verbose: bool = False
    """Enable detailed logging."""


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.

    Returns:
        AppConfig with all settings

    Raises:
        ValueError: Missing required configuration
    """
    load_dotenv()

    # Auto-detect OpenRouter: prioritize OPENROUTER_API_KEY, fallback to OPENAI_API_KEY
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if openrouter_key:
        # Using OpenRouter
        api_key = openrouter_key
        base_url = "https://openrouter.ai/api/v1"
    elif openai_key:
        # Using OpenAI
        api_key = openai_key
        base_url = None
    else:
        raise ValueError("OPENROUTER_API_KEY or OPENAI_API_KEY environment variable is required")

    cohere_key = os.getenv("COHERE_API_KEY")
    if not cohere_key:
        raise ValueError("COHERE_API_KEY environment variable is required")

    qdrant_url = os.getenv("QDRANT_URL")
    if not qdrant_url:
        raise ValueError("QDRANT_URL environment variable is required")

    qdrant_key = os.getenv("QDRANT_API_KEY")
    if not qdrant_key:
        raise ValueError("QDRANT_API_KEY environment variable is required")

    # Get agent model from env (default to OpenRouter free model)
    agent_model = os.getenv("AGENT_MODEL")
    if not agent_model:
        # Auto-detect: use OpenRouter model if using OpenRouter
        # Using verified free model that works well
        agent_model = "mistralai/mistral-7b-instruct:free" if openrouter_key else "gpt-4o-mini"

    # Build and return config
    return AppConfig(
        openai_api_key=api_key,
        openai_base_url=base_url,
        cohere_api_key=cohere_key,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_key,
        collection_name=os.getenv("COLLECTION_NAME", "web_documents"),
        agent_model=agent_model,
        agent_temperature=float(os.getenv("AGENT_TEMPERATURE", "0.7")),
        agent_max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "1000")),
        agent_system_prompt=os.getenv("AGENT_SYSTEM_PROMPT"),
        top_k_retrieval=int(os.getenv("TOP_K_RETRIEVAL", "5")),
        retrieval_score_threshold=float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.3")),
        verbose=os.getenv("VERBOSE", "false").lower() == "true"
    )


def get_config() -> AppConfig:
    """Get cached config instance."""
    if not hasattr(get_config, "_cached_config"):
        get_config._cached_config = load_config()
    return get_config._cached_config
