"""
Retrieval tool for RAG agent.

Handles vector search operations on Qdrant with Cohere embeddings.
"""

import asyncio
import logging
from typing import Optional
from qdrant_client import QdrantClient, models
import cohere
from dotenv import load_dotenv

from config import AppConfig
from agent_types import RetrievalError


logger = logging.getLogger(__name__)


async def search(
    query: str,
    config: AppConfig,
    top_k: Optional[int] = None,
    score_threshold: Optional[float] = None
) -> SearchResponse:
    """
    Search Qdrant for semantically similar chunks.

    Args:
        query: Natural language search query
        config: Application configuration
        top_k: Number of chunks to retrieve (default from config)
        score_threshold: Minimum similarity score (default from config)

    Returns:
        SearchResponse with ranked results

    Raises:
        RetrievalError: On search failure
    """
    # Use config defaults if not specified
    top_k = top_k if top_k is not None else config.top_k_retrieval
    score_threshold = score_threshold if score_threshold is not None else config.retrieval_score_threshold

    logger.info(f"Searching Qdrant for: '{query[:50]}...'")

    # Initialize Cohere client for embeddings
    cohere_client = cohere.AsyncClient(api_key=config.cohere_api_key)

    # Initialize Qdrant client
    qdrant_client = QdrantClient(
        url=config.qdrant_url,
        api_key=config.qdrant_api_key
    )

    try:
        # Generate query embedding
        embed_response = await cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        )

        query_vector = embed_response.embeddings[0]
        logger.debug(f"Generated query embedding: {len(query_vector)} dimensions")

        # Search Qdrant
        query_filter = None  # Could add filtering here

        results = qdrant_client.query_points(
            collection_name=config.collection_name,
            query=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter,
            with_payload=True
        ).points

        logger.info(f"Found {len(results)} results in Qdrant")

        # Format results
        chunks = []
        for result in results:
            payload = result.payload
            chunks.append(RetrievalResult(
                chunk_id=str(result.id),
                chunk_text=payload.get("chunk_text", ""),
                url=payload.get("url", ""),
                title=payload.get("title"),
                similarity_score=result.score,
                chunk_index=payload.get("chunk_index", 0)
            ))

        return SearchResponse(
            query=query,
            results=chunks,
            total_count=len(chunks),
            top_score=chunks[0].similarity_score if chunks else 0.0,
            avg_score=sum(c.similarity_score for c in chunks) / len(chunks) if chunks else 0.0
        )

    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise RetrievalError(f"Search operation failed: {str(e)}")
