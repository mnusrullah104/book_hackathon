# Data Model: RAG Retrieval Validation and Testing

**Feature**: 003-rag-retrieval-validation
**Date**: 2025-12-25
**Purpose**: Define data structures for retrieval queries, results, and validation

## Overview

This system queries the Qdrant vector database for semantically similar chunks, validates embedding consistency, and verifies metadata completeness. Data flows through four core entities: QueryRequest → query embedding → Qdrant search → RetrievalResult.

## Entity Definitions

### 1. QueryRequest

**Purpose**: Input parameters for a retrieval query

**Attributes**:
- `query_text` (str): Natural language search query
- `top_k` (int): Number of results to return (default: 5)
- `score_threshold` (float): Minimum similarity score (default: 0.0, range: 0.0-1.0)
- `url_filter` (str | None): Optional URL pattern to filter results (e.g., "module-1")
- `include_vectors` (bool): Whether to return embedding vectors (default: False)
- `collection_name` (str): Qdrant collection to search (default: "web_documents")

**Validation Rules**:
- `query_text` must not be empty
- `top_k` must be between 1 and 100
- `score_threshold` must be between 0.0 and 1.0
- `collection_name` must be non-empty

**Lifecycle**: Created for each query request, immutable during execution

---

### 2. RetrievedChunk

**Purpose**: Represents a single search result from Qdrant

**Attributes**:
- `chunk_id` (str): Qdrant point ID
- `similarity_score` (float): COSINE similarity (0.0-1.0, higher = more similar)
- `chunk_text` (str): Full text content of the chunk
- `url` (str): Source URL of the document
- `title` (str | None): Document title (may be None)
- `chunk_index` (int): Position in original document (0-based)
- `token_count` (int): Number of tokens in chunk
- `timestamp` (str): ISO 8601 ingestion timestamp
- `chunk_config` (dict): Chunking parameters used during ingestion
- `model_name` (str): Embedding model identifier
- `dimension` (int): Vector dimensions
- `vector` (List[float] | None): Embedding vector (only if include_vectors=True)

**Relationships**:
- Retrieved from Qdrant via search() API
- Corresponds to a stored QdrantPoint from ingestion pipeline

**Validation Rules**:
- `similarity_score` must be between 0.0 and 1.0
- `chunk_text` must not be empty
- `chunk_index` must be non-negative
- `dimension` must be 1024 (for Cohere embed-english-v3.0)
- If `vector` present, length must equal `dimension`

**Lifecycle**: Created from Qdrant ScoredPoint response, returned to caller

---

### 3. RetrievalResult

**Purpose**: Complete result set from a retrieval query

**Attributes**:
- `query` (str): Original query text
- `chunks` (List[RetrievedChunk]): Retrieved chunks ordered by similarity (high to low)
- `total_results` (int): Number of chunks returned
- `execution_time_seconds` (float): Query duration
- `top_score` (float): Highest similarity score in results
- `avg_score` (float): Average similarity across results

**Relationships**:
- Contains multiple RetrievedChunk objects
- Corresponds to one QueryRequest

**Validation Rules**:
- `total_results` must equal len(chunks)
- `chunks` must be ordered by similarity_score descending
- `top_score` must be >= all individual chunk scores
- `execution_time_seconds` must be positive

**Lifecycle**: Created after Qdrant search completes, returned as final result

---

### 4. ValidationReport

**Purpose**: Results from automated validation checks

**Attributes**:
- `test_name` (str): Name of validation test (e.g., "Dimension Consistency Check")
- `status` (str): "PASS" or "FAIL"
- `total_checks` (int): Number of items validated
- `passed_checks` (int): Number of successful validations
- `failed_checks` (int): Number of failures
- `issues_found` (List[str]): Specific problems detected
- `execution_time_seconds` (float): Validation duration

**Relationships**:
- Independent validation entity (not tied to specific queries)
- May reference RetrievedChunk or raw Qdrant data

**Validation Rules**:
- `passed_checks` + `failed_checks` must equal `total_checks`
- `status` is "PASS" if `failed_checks == 0`, else "FAIL"
- `issues_found` length should match `failed_checks`

**Lifecycle**: Created during validation runs, can be logged or displayed

---

## Data Flow Diagram

```
┌─────────────────┐
│  QueryRequest   │
│  (query_text)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Embedding │ Generate via Cohere API
│ (1024-dim)      │ input_type="search_query"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Qdrant Search   │ search() with COSINE distance
│ (similarity)    │ Returns ScoredPoint objects
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RetrievedChunk[]│ Parse results into chunks
│ (with metadata) │ Extract payload, score, id
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ RetrievalResult │ Aggregate into final result
│ (ordered list)  │ Calculate stats, execution time
└─────────────────┘
```

---

## Qdrant Query Patterns

### Basic Similarity Search

```python
# Query embedding
query_embedding = await embed_query("ROS 2 fundamentals", cohere_client)

# Search Qdrant
results = client.search(
    collection_name="web_documents",
    query_vector=query_embedding,
    limit=5,
    with_payload=True,
    with_vectors=False  # Don't return vectors unless needed
)

# Parse results
chunks = [
    RetrievedChunk(
        chunk_id=r.id,
        similarity_score=r.score,
        chunk_text=r.payload["chunk_text"],
        url=r.payload["url"],
        ...
    )
    for r in results
]
```

### Filtered Search (User Story 2)

```python
# Search with URL filter for Module 1 only
results = client.search(
    collection_name="web_documents",
    query_vector=query_embedding,
    limit=5,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="url",
                match=models.MatchText(text="module-1")
            )
        ]
    ),
    with_payload=True
)
```

---

## Validation Test Patterns

### 1. Dimension Consistency Test

```python
# Get all points with vectors
points = client.scroll(
    collection_name="web_documents",
    limit=1000,
    with_vectors=True
)[0]

# Validate dimensions
for point in points:
    assert len(point.vector) == 1024, f"Invalid dimension: {len(point.vector)}"
```

### 2. Metadata Completeness Test

```python
# Get all points with metadata
points = client.scroll(
    collection_name="web_documents",
    limit=1000,
    with_payload=True
)[0]

# Validate required fields
REQUIRED = ["url", "chunk_text", "timestamp", "chunk_index"]
missing_count = 0

for point in points:
    for field in REQUIRED:
        if field not in point.payload:
            missing_count += 1
            print(f"Missing {field} in point {point.id}")

assert missing_count == 0, f"{missing_count} chunks missing required fields"
```

### 3. Embedding Consistency Test

```python
# Embed same text twice
text = "test document about robotics"
embedding1 = await embed_query(text, cohere_client)
embedding2 = await embed_query(text, cohere_client)

# Calculate cosine similarity
from numpy import dot
from numpy.linalg import norm
similarity = dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2))

assert similarity > 0.99, f"Consistency check failed: {similarity}"
```

---

## Error States & Handling

| Operation | Error State | Handling |
|-----------|------------|----------|
| QueryRequest | Empty query_text | Raise ValueError with guidance |
| QueryRequest | Invalid top_k | Raise ValueError with valid range |
| Query Embedding | Cohere API failure | Raise CohereAPIError after retries |
| Qdrant Search | Collection not found | Raise QdrantConnectionError |
| Qdrant Search | No results | Return empty RetrievalResult (not an error) |
| Metadata Validation | Missing required field | Log warning, include in ValidationReport |
| Dimension Validation | Wrong vector size | Log error, include in ValidationReport |

---

## Future Extensions (Out of Scope for MVP)

- **Re-ranking**: Post-retrieval relevance scoring with cross-encoder
- **Hybrid search**: Combine vector similarity with keyword matching
- **Query expansion**: Automatic query reformulation for better recall
- **Caching**: Cache frequent query embeddings to reduce API calls
- **Batch querying**: Support multiple queries in one call

---

## Validation Checklist

- [x] All entities have clear purpose and lifecycle
- [x] Validation rules are testable
- [x] Qdrant search patterns documented
- [x] Error states defined
- [x] Test patterns for each validation type provided
- [x] Metadata requirements specified (required vs. optional)
- [x] Similarity score interpretation guidelines defined
