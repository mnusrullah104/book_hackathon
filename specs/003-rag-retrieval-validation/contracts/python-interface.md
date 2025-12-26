# Python Interface Contract: RAG Retrieval Validation

**Feature**: 003-rag-retrieval-validation
**Date**: 2025-12-25
**Purpose**: Define programmatic interface for querying and validating the RAG pipeline

## Overview

This module exposes retrieval and validation functions in `backend/retrieve.py` for querying Qdrant vector database and validating ingestion pipeline correctness.

## Public Interface

### 1. Main Retrieval Function

```python
async def search(
    query_text: str,
    *,
    top_k: int = 5,
    score_threshold: float = 0.0,
    url_filter: str | None = None,
    include_vectors: bool = False,
    cohere_api_key: str | None = None,
    qdrant_url: str | None = None,
    qdrant_api_key: str | None = None,
    collection_name: str = "web_documents",
    verbose: bool = True
) -> RetrievalResult:
    """
    Search Qdrant collection for semantically similar chunks.

    Args:
        query_text: Natural language search query
        top_k: Number of results to return (1-100)
        score_threshold: Minimum similarity score (0.0-1.0)
        url_filter: Optional URL pattern to filter results (e.g., "module-1")
        include_vectors: Return embedding vectors in results
        cohere_api_key: Cohere API key (defaults to COHERE_API_KEY env var)
        qdrant_url: Qdrant instance URL (defaults to QDRANT_URL env var)
        qdrant_api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
        collection_name: Target Qdrant collection
        verbose: Enable detailed logging

    Returns:
        RetrievalResult with ranked chunks and metadata

    Raises:
        ValueError: Invalid parameters (empty query, invalid top_k)
        ConfigurationError: Missing or invalid API credentials
        QdrantConnectionError: Cannot connect to Qdrant
        CohereAPIError: Query embedding generation failed

    Example:
        >>> result = await search(
        ...     "How do I set up ROS 2 for humanoids?",
        ...     top_k=5,
        ...     score_threshold=0.7
        ... )
        >>> print(f"Found {result.total_results} chunks")
        >>> for chunk in result.chunks:
        ...     print(f"  {chunk.url}: {chunk.similarity_score:.3f}")
    """
```

---

### 2. Validation Functions

```python
async def validate_pipeline(
    *,
    cohere_api_key: str | None = None,
    qdrant_url: str | None = None,
    qdrant_api_key: str | None = None,
    collection_name: str = "web_documents",
    verbose: bool = True
) -> ValidationReport:
    """
    Run automated validation checks on the RAG pipeline.

    Validates:
    - Vector dimensions (all 1024-dim)
    - Metadata completeness (required fields present)
    - Embedding consistency (identical text >0.99 similarity)
    - No unintentional duplicate URLs

    Args:
        cohere_api_key: Cohere API key (defaults to env var)
        qdrant_url: Qdrant instance URL (defaults to env var)
        qdrant_api_key: Qdrant API key (defaults to env var)
        collection_name: Target collection
        verbose: Enable detailed output

    Returns:
        ValidationReport with pass/fail status and issue details

    Raises:
        ConfigurationError: Missing credentials
        QdrantConnectionError: Cannot connect to Qdrant

    Example:
        >>> report = await validate_pipeline(verbose=True)
        >>> print(f"Status: {report.status}")
        >>> print(f"Passed: {report.passed_checks}/{report.total_checks}")
        >>> if report.failed_checks > 0:
        ...     for issue in report.issues_found:
        ...         print(f"  - {issue}")
    """
```

---

### 3. Result Types

```python
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

    title: str | None
    """Document title (may be None)."""

    chunk_index: int
    """Position in original document (0-based)."""

    token_count: int
    """Number of tokens in this chunk."""

    timestamp: str
    """ISO 8601 ingestion timestamp."""

    chunk_config: dict
    """Chunking parameters: chunk_size, chunk_overlap."""

    model_name: str
    """Embedding model identifier."""

    dimension: int
    """Vector dimensions."""

    vector: List[float] | None = None
    """Embedding vector (only if include_vectors=True)."""


@dataclass
class RetrievalResult:
    """Complete result set from a retrieval query."""

    query: str
    """Original query text."""

    chunks: List[RetrievedChunk]
    """Retrieved chunks ordered by similarity (high to low)."""

    total_results: int
    """Number of chunks returned."""

    execution_time_seconds: float
    """Query duration."""

    top_score: float
    """Highest similarity score in results."""

    avg_score: float
    """Average similarity across results."""


@dataclass
class ValidationReport:
    """Results from automated validation checks."""

    test_name: str
    """Name of validation test."""

    status: str
    """PASS or FAIL."""

    total_checks: int
    """Number of items validated."""

    passed_checks: int
    """Number of successful validations."""

    failed_checks: int
    """Number of failures."""

    issues_found: List[str]
    """Specific problems detected."""

    execution_time_seconds: float
    """Validation duration."""

    @property
    def pass_rate(self) -> float:
        """Percentage of checks that passed."""
        return (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0.0
```

---

## Usage Examples

### Example 1: Simple Query

```python
import asyncio
from retrieve import search

async def test_basic_search():
    result = await search(
        "How do I set up ROS 2 for humanoid robots?",
        top_k=5,
        verbose=True
    )

    print(f"Query: {result.query}")
    print(f"Found {result.total_results} chunks")
    print(f"Top score: {result.top_score:.3f}")
    print(f"Avg score: {result.avg_score:.3f}")

    for i, chunk in enumerate(result.chunks, 1):
        print(f"\n{i}. [{chunk.similarity_score:.3f}] {chunk.title}")
        print(f"   URL: {chunk.url}")
        print(f"   Chunk {chunk.chunk_index}: {chunk.chunk_text[:100]}...")

asyncio.run(test_basic_search())
```

**Expected Output**:
```
Query: How do I set up ROS 2 for humanoid robots?
Found 5 chunks
Top score: 0.872
Avg score: 0.789

1. [0.872] 1.1 ROS 2 Fundamentals | AI-Native Robotics Book
   URL: https://book-writing-hackathon1.vercel.app/docs/module-1/ros2-fundamentals
   Chunk 0: ROS 2 is the next generation of the Robot Operating System...

2. [0.834] 1.2 Python Agents with rclpy | AI-Native Robotics Book
   URL: https://book-writing-hackathon1.vercel.app/docs/module-1/python-agents-rclpy
   Chunk 1: Building intelligent agents for humanoid robots requires...
```

---

### Example 2: Filtered Search

```python
import asyncio
from retrieve import search

async def test_filtered_search():
    # Search only Module 3 (NVIDIA Isaac) content
    result = await search(
        "Isaac Sim for robot simulation",
        top_k=3,
        url_filter="isaac-robot-brain",
        score_threshold=0.7,
        verbose=True
    )

    print(f"Found {result.total_results} chunks from Module 3")
    for chunk in result.chunks:
        print(f"  [{chunk.similarity_score:.3f}] {chunk.title}")

asyncio.run(test_filtered_search())
```

---

### Example 3: Validation

```python
import asyncio
from retrieve import validate_pipeline

async def test_validation():
    report = await validate_pipeline(verbose=True)

    print(f"Validation: {report.test_name}")
    print(f"Status: {report.status}")
    print(f"Passed: {report.passed_checks}/{report.total_checks}")
    print(f"Pass Rate: {report.pass_rate:.1f}%")

    if report.failed_checks > 0:
        print(f"\nIssues Found:")
        for issue in report.issues_found:
            print(f"  - {issue}")

asyncio.run(test_validation())
```

**Expected Output**:
```
Validation: RAG Pipeline Validation
Status: PASS
Passed: 4/4
Pass Rate: 100.0%
```

---

### Example 4: End-to-End Test

```python
import asyncio
from main import main as ingest
from retrieve import search

async def test_end_to_end():
    # Step 1: Ingest test URL
    test_url = "https://example.com/test-doc"
    ingest_result = await ingest([test_url], skip_duplicates=False)

    print(f"Ingested: {ingest_result.total_chunks} chunks")

    # Step 2: Query for test content
    result = await search(
        "content from test document",
        top_k=5
    )

    # Step 3: Verify test chunks are retrievable
    test_chunks = [c for c in result.chunks if test_url in c.url]
    print(f"Retrieved {len(test_chunks)} chunks from test URL")

    assert len(test_chunks) > 0, "Test document not found in search results"
    assert test_chunks[0].similarity_score > 0.9, "Low similarity for test doc"

    print("✓ End-to-end test PASSED")

asyncio.run(test_end_to_end())
```

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Query embedding generation | 200-500ms | Cohere API call (single text) |
| Qdrant vector search | 50-200ms | Depends on collection size |
| Metadata retrieval | +10-50ms | Included in search time |
| **Total per query (avg)** | 300-700ms | Well under 1s target |

**Scaling**:
- Collection size (109 chunks): Negligible impact on search speed
- Collection size (10,000+ chunks): HNSW index keeps search <200ms
- Concurrent queries: Supported natively by async implementation

---

## Versioning & Compatibility

**Interface Version**: 1.0.0

**Compatibility with Ingestion**:
- Must use same Cohere model (embed-english-v3.0)
- Must use same collection (web_documents)
- Must use same vector dimensions (1024)
- Compatible with all metadata fields from ingestion

**Breaking Changes Policy**:
- Function signature changes: Major version bump
- New optional parameters: Minor version bump
- Bug fixes: Patch version bump
