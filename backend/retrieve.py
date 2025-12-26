"""
RAG Retrieval Validation and Testing

Query Qdrant vector database for semantically similar chunks, validate metadata
completeness, and verify end-to-end ingestion-to-retrieval pipeline correctness.
"""

import os
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import time

# Embeddings and vector search
import cohere
from qdrant_client import QdrantClient, models
from dotenv import load_dotenv

# Import exceptions from main.py
import sys
sys.path.insert(0, os.path.dirname(__file__))
from main import ConfigurationError, QdrantConnectionError, CohereAPIError


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class RetrievedChunk:
    """A single search result from Qdrant."""

    chunk_id: str
    """Qdrant point ID."""

    similarity_score: float
    """COSINE similarity score (0.0-1.0, higher = more similar)."""

    chunk_text: str
    """Full text content of the chunk."""

    url: str
    """Source URL of the document."""

    title: Optional[str]
    """Document title (may be None)."""

    chunk_index: int
    """Position in original document (0-based)."""

    token_count: int
    """Number of tokens in this chunk."""

    timestamp: str
    """ISO 8601 ingestion timestamp."""

    chunk_config: Dict[str, Any]
    """Chunking parameters: chunk_size, chunk_overlap."""

    model_name: str
    """Embedding model identifier."""

    dimension: int
    """Vector dimensions."""

    vector: Optional[List[float]] = None
    """Embedding vector (only if include_vectors=True)."""


@dataclass
class RetrievalResult:
    """Complete result set from a retrieval query."""

    query: str
    """Original query text."""

    chunks: List[RetrievedChunk] = field(default_factory=list)
    """Retrieved chunks ordered by similarity (high to low)."""

    total_results: int = 0
    """Number of chunks returned."""

    execution_time_seconds: float = 0.0
    """Query duration."""

    top_score: float = 0.0
    """Highest similarity score in results."""

    avg_score: float = 0.0
    """Average similarity across results."""


@dataclass
class ValidationReport:
    """Results from automated validation checks."""

    test_name: str
    """Name of validation test."""

    status: str
    """PASS or FAIL."""

    total_checks: int = 0
    """Number of items validated."""

    passed_checks: int = 0
    """Number of successful validations."""

    failed_checks: int = 0
    """Number of failures."""

    issues_found: List[str] = field(default_factory=list)
    """Specific problems detected."""

    execution_time_seconds: float = 0.0
    """Validation duration."""

    @property
    def pass_rate(self) -> float:
        """Percentage of checks that passed."""
        return (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0.0


# =============================================================================
# CONFIGURATION & LOGGING
# =============================================================================

def load_retrieval_config(
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
    collection_name: str = "web_documents"
) -> tuple:
    """
    Load configuration from environment variables with fallbacks.

    Args:
        cohere_api_key: Cohere API key (overrides env var)
        qdrant_url: Qdrant instance URL (overrides env var)
        qdrant_api_key: Qdrant API key (overrides env var)
        collection_name: Target collection name

    Returns:
        Tuple of (cohere_api_key, qdrant_url, qdrant_api_key, collection_name)

    Raises:
        ConfigurationError: If required credentials are missing
    """
    load_dotenv()

    # Load API credentials with fallbacks
    cohere_key = cohere_api_key or os.getenv("COHERE_API_KEY")
    qdrant_url_val = qdrant_url or os.getenv("QDRANT_URL")
    qdrant_key = qdrant_api_key or os.getenv("QDRANT_API_KEY")

    # Validate required credentials
    if not cohere_key:
        raise ConfigurationError(
            "COHERE_API_KEY not provided. Set environment variable or pass as parameter."
        )
    if not qdrant_url_val:
        raise ConfigurationError(
            "QDRANT_URL not provided. Set environment variable or pass as parameter."
        )
    if not qdrant_key:
        raise ConfigurationError(
            "QDRANT_API_KEY not provided. Set environment variable or pass as parameter."
        )

    return cohere_key, qdrant_url_val, qdrant_key, collection_name


def setup_retrieval_logging(verbose: bool = True):
    """
    Configure logging for retrieval operations.

    Args:
        verbose: Enable INFO level logging (default: True)
    """
    level = logging.INFO if verbose else logging.ERROR
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


logger = logging.getLogger(__name__)


# =============================================================================
# PHASE 3: USER STORY 1 - CORE RETRIEVAL FUNCTIONS
# =============================================================================

async def embed_query(
    query_text: str,
    cohere_client: cohere.AsyncClient,
    model: str = "embed-english-v3.0"
) -> List[float]:
    """
    Generate query embedding using Cohere with search_query input type.

    Args:
        query_text: Natural language query
        cohere_client: Cohere async client
        model: Cohere model identifier

    Returns:
        Query embedding vector (1024-dim for embed-english-v3.0)

    Raises:
        CohereAPIError: On embedding generation failure
    """
    logger.info(f"Generating query embedding for: '{query_text[:50]}...'")

    try:
        response = await cohere_client.embed(
            texts=[query_text],
            model=model,
            input_type="search_query"  # Different from ingestion's "search_document"
        )
        embedding = response.embeddings[0]
        logger.info(f"Generated query embedding, dim={len(embedding)}")
        return embedding

    except Exception as e:
        logger.error(f"Cohere API error: {e}")
        raise CohereAPIError(f"Failed to generate query embedding: {e}")


def parse_search_results(
    results: List[Any],
    include_vectors: bool = False
) -> List[RetrievedChunk]:
    """
    Convert Qdrant ScoredPoint objects to RetrievedChunk data classes.

    Args:
        results: List of ScoredPoint objects from Qdrant
        include_vectors: Whether to include embedding vectors

    Returns:
        List of RetrievedChunk objects with metadata
    """
    chunks = []

    for result in results:
        # Extract metadata from payload
        payload = result.payload

        chunk = RetrievedChunk(
            chunk_id=str(result.id),
            similarity_score=result.score,
            chunk_text=payload.get("chunk_text", ""),
            url=payload.get("url", ""),
            title=payload.get("title"),
            chunk_index=payload.get("chunk_index", 0),
            token_count=payload.get("token_count", 0),
            timestamp=payload.get("timestamp", ""),
            chunk_config=payload.get("chunk_config", {}),
            model_name=payload.get("model_name", ""),
            dimension=payload.get("dimension", 1024),
            vector=result.vector if (include_vectors and hasattr(result, 'vector')) else None
        )
        chunks.append(chunk)

    logger.debug(f"Parsed {len(chunks)} search results")
    return chunks


async def search_qdrant(
    query_vector: List[float],
    client: QdrantClient,
    collection_name: str,
    top_k: int = 5,
    score_threshold: float = 0.0,
    url_filter: Optional[str] = None,
    include_vectors: bool = False
) -> List[Any]:
    """
    Search Qdrant collection using vector similarity.

    Args:
        query_vector: Query embedding vector
        client: QdrantClient instance
        collection_name: Target collection
        top_k: Number of results to return
        score_threshold: Minimum similarity score
        url_filter: Optional URL pattern filter
        include_vectors: Return embedding vectors

    Returns:
        List of ScoredPoint objects from Qdrant

    Raises:
        QdrantConnectionError: On search failure
    """
    logger.info(f"Searching Qdrant collection '{collection_name}', top_k={top_k}, threshold={score_threshold}")

    try:
        # Build filter if URL pattern provided
        query_filter = None
        if url_filter:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="url",
                        match=models.MatchText(text=url_filter)
                    )
                ]
            )
            logger.info(f"Applying URL filter: {url_filter}")

        # Execute search using query_points
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=include_vectors
        ).points

        logger.info(f"Found {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Qdrant search error: {e}")
        raise QdrantConnectionError(f"Failed to search Qdrant: {e}")


# =============================================================================
# PLACEHOLDER FOR PHASE 4-6 FUNCTIONS
# =============================================================================

# TODO: Phase 4 - User Story 2 functions will be added here
# TODO: Phase 5 - User Story 3 functions will be added here
# TODO: Phase 6 - User Story 4 functions will be added here


# =============================================================================
# MAIN SEARCH FUNCTION (Placeholder)
# =============================================================================

async def search(
    query_text: str,
    *,
    top_k: int = 5,
    score_threshold: float = 0.0,
    url_filter: Optional[str] = None,
    include_vectors: bool = False,
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
    collection_name: str = "web_documents",
    verbose: bool = True
) -> RetrievalResult:
    """
    Search Qdrant collection for semantically similar chunks.

    Args:
        query_text: Natural language search query
        top_k: Number of results to return (1-100)
        score_threshold: Minimum similarity score (0.0-1.0)
        url_filter: Optional URL pattern to filter results
        include_vectors: Return embedding vectors in results
        cohere_api_key: Cohere API key (defaults to env var)
        qdrant_url: Qdrant instance URL (defaults to env var)
        qdrant_api_key: Qdrant API key (defaults to env var)
        collection_name: Target Qdrant collection
        verbose: Enable detailed logging

    Returns:
        RetrievalResult with ranked chunks and metadata

    Raises:
        ValueError: Invalid parameters
        ConfigurationError: Missing API credentials
        QdrantConnectionError: Cannot connect to Qdrant
        CohereAPIError: Query embedding generation failed
    """
    start_time = time.time()
    setup_retrieval_logging(verbose)
    logger.info(f"=== Retrieval Query: '{query_text}' ===")

    # Validate input parameters
    if not query_text or not query_text.strip():
        raise ValueError("query_text must not be empty")
    if not 1 <= top_k <= 100:
        raise ValueError(f"top_k must be between 1 and 100, got {top_k}")
    if not 0.0 <= score_threshold <= 1.0:
        raise ValueError(f"score_threshold must be between 0.0 and 1.0, got {score_threshold}")

    # Load configuration
    cohere_key, qdrant_url_val, qdrant_key, coll_name = load_retrieval_config(
        cohere_api_key, qdrant_url, qdrant_api_key, collection_name
    )

    logger.info(f"Configuration: collection={coll_name}, top_k={top_k}, threshold={score_threshold}")

    # Initialize clients
    cohere_client = cohere.AsyncClient(api_key=cohere_key)
    qdrant_client = QdrantClient(url=qdrant_url_val, api_key=qdrant_key)

    # Step 1: Generate query embedding
    query_vector = await embed_query(query_text, cohere_client)

    # Step 2: Search Qdrant
    search_results = await search_qdrant(
        query_vector,
        qdrant_client,
        coll_name,
        top_k,
        score_threshold,
        url_filter,
        include_vectors
    )

    # Step 3: Parse results
    chunks = parse_search_results(search_results, include_vectors)

    # Step 4: Calculate statistics
    total = len(chunks)
    top_score = chunks[0].similarity_score if chunks else 0.0
    avg_score = sum(c.similarity_score for c in chunks) / total if total > 0 else 0.0
    exec_time = time.time() - start_time

    # Build result
    result = RetrievalResult(
        query=query_text,
        chunks=chunks,
        total_results=total,
        execution_time_seconds=exec_time,
        top_score=top_score,
        avg_score=avg_score
    )

    logger.info(f"=== Query Complete: {total} results, top_score={top_score:.3f}, avg={avg_score:.3f}, time={exec_time:.2f}s ===")

    return result


if __name__ == "__main__":
    # CLI entry point for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python retrieve.py <query>")
        print("Example: python retrieve.py 'How do I set up ROS 2 for humanoids?'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    result = asyncio.run(search(query, verbose=True))

    print(f"\n[QUERY] {result.query}")
    print(f"[RESULTS] {result.total_results} chunks")
    print(f"[TOP SCORE] {result.top_score:.3f}")
    print(f"[AVG SCORE] {result.avg_score:.3f}")
    print(f"[TIME] {result.execution_time_seconds:.2f}s")
