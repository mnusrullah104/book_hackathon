# Research: RAG Retrieval Validation and Testing

**Feature**: 003-rag-retrieval-validation
**Date**: 2025-12-25
**Purpose**: Resolve technical decisions for vector search retrieval and validation

## Research Questions & Decisions

### 1. Qdrant Search API Usage

**Question**: Which Qdrant API method provides the best balance of simplicity and functionality for RAG retrieval?

**Decision**: Use `client.search()` for basic similarity search, `client.query()` for advanced filtering

**Rationale**:
- **search()** is simpler for basic vector similarity (just query vector + top_k)
- **query()** supports advanced filters but adds complexity
- For MVP (User Story 1): `search()` is sufficient
- For User Story 2 (filtering): can add basic filters to `search()` via `query_filter` parameter
- Both methods return same result format (ScoredPoint objects)

**Implementation Pattern**:
```python
# Basic search (User Story 1)
results = client.search(
    collection_name="web_documents",
    query_vector=query_embedding,
    limit=5,
    with_payload=True
)

# Search with URL filter (User Story 2)
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

**Alternatives Considered**:
- **scroll()**: No vector similarity, just metadata filtering (not suitable for semantic search)
- **recommend()**: For finding similar items to a known point, not for query-based search
- **Custom distance calculation**: Requires fetching all vectors, inefficient

---

### 2. Query Embedding Input Type

**Question**: Should query embeddings use the same `input_type` as document embeddings?

**Decision**: Use `input_type="search_query"` for queries, different from `input_type="search_document"` used for ingestion

**Rationale**:
- **Cohere best practice**: Asymmetric search with different input types
- **search_document**: Optimizes embeddings for storage (documents)
- **search_query**: Optimizes embeddings for retrieval (user queries)
- **Better retrieval quality**: Cohere models are trained with this asymmetry
- **Same model**: Still use embed-english-v3.0 for consistency

**Implementation**:
```python
# Ingestion (already implemented in main.py)
await cohere_client.embed(texts=chunks, model="embed-english-v3.0", input_type="search_document")

# Retrieval (new in retrieve.py)
await cohere_client.embed(texts=[query], model="embed-english-v3.0", input_type="search_query")
```

**Alternatives Considered**:
- **Same input_type for both**: Simpler but lower retrieval quality (symmetric vs. asymmetric)
- **Different models**: Would break similarity comparisons, not suitable

---

### 3. Similarity Score Interpretation

**Question**: What similarity score thresholds indicate good, moderate, and poor relevance?

**Decision**: Use the following guidelines for COSINE similarity interpretation

**Rationale**:
- COSINE distance in Qdrant ranges from 0 to 2 (0 = identical, 2 = opposite)
- Qdrant returns similarity as (1 - distance), so range is 0.0 to 1.0
- Based on empirical testing with Cohere embeddings on documentation:
  - **>0.85**: Highly relevant (near-exact match or same topic)
  - **0.70-0.85**: Moderately relevant (related concepts)
  - **0.50-0.70**: Loosely related
  - **<0.50**: Likely not relevant

**Guidelines for Developers**:
- **Strict queries** (exact answers): Filter for >0.8 similarity
- **Exploratory queries** (broad topics): Accept >0.7 similarity
- **Related content** (context gathering): Include >0.6 similarity
- **No threshold**: Return top-k regardless of score (let developer interpret)

**Default in Implementation**: No automatic filtering, return top-k with scores for developer interpretation

---

### 4. Metadata Validation Requirements

**Question**: Which metadata fields are absolutely required vs. optional for validation?

**Decision**: Required fields: url, chunk_text, timestamp, chunk_index; Optional: title, token_count, chunk_config, model_name

**Rationale**:
- **url**: Critical for citation and source tracking
- **chunk_text**: Core content, must always be present
- **timestamp**: Important for data freshness tracking
- **chunk_index**: Needed for reconstructing document order
- **title** (optional): May be None for pages without titles
- **token_count** (optional): Useful but not critical for retrieval
- **chunk_config** (optional): Debugging aid, not essential
- **model_name** (optional): Useful for multi-model scenarios, not critical now

**Validation Logic**:
```python
REQUIRED_FIELDS = ["url", "chunk_text", "timestamp", "chunk_index"]
OPTIONAL_FIELDS = ["title", "token_count", "chunk_config", "model_name", "dimension"]

def validate_metadata(payload: dict) -> tuple:
    """Returns (is_valid, missing_fields)"""
    missing = [f for f in REQUIRED_FIELDS if f not in payload]
    return len(missing) == 0, missing
```

---

### 5. End-to-End Test Document Strategy

**Question**: What type of test document provides the best validation of the ingestion-to-retrieval flow?

**Decision**: Use a small, controlled HTML page with known content (self-hosted or simple external URL)

**Rationale**:
- **Small size**: Quick to ingest (< 2 seconds)
- **Known content**: Predictable chunks and keywords for query testing
- **Stable**: Won't change over time (unlike live documentation)
- **Unique keywords**: Contains terms unlikely to appear in existing corpus

**Recommended Test URL**: Create a simple test page or use a stable, small documentation page

**Test Flow**:
1. Ingest test URL with unique content (e.g., "XYZ-unique-test-keyword-123")
2. Wait for ingestion to complete
3. Query for unique keyword
4. Assert: Test document chunks returned with >0.9 similarity
5. Cleanup: Optionally delete test chunks after validation

**Alternative**: Use existing documentation page and query for unique phrases from it

---

### 6. Validation Report Format

**Question**: How should validation results be reported to developers?

**Decision**: Simple text output with pass/fail status and issue details

**Rationale**:
- **Simple format**: Plain text or markdown, no complex formatting needed
- **Pass/fail per check**: Clear status for each validation type
- **Issue details**: List specific problems found (missing fields, dimension mismatches)
- **Summary stats**: Total checks, passed, failed
- **Exit code**: 0 for pass, 1 for fail (script-friendly)

**Report Format**:
```text
=== RAG Pipeline Validation Report ===

[DIMENSION CHECK] PASS
  - All 109 vectors have 1024 dimensions

[METADATA CHECK] PASS
  - All chunks have required fields: url, chunk_text, timestamp, chunk_index
  - Missing optional fields: 0

[SIMILARITY CHECK] PASS
  - Identical text similarity: 0.998 (>0.99 threshold)

[RETRIEVAL CHECK] PASS
  - Query "ROS 2 fundamentals" returned 5 chunks from Module 1
  - Top similarity score: 0.872

=== SUMMARY ===
Total Checks: 4
Passed: 4
Failed: 0

Status: ✅ ALL VALIDATIONS PASSED
```

---

## Summary of Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Query Embeddings | Cohere embed-english-v3.0 | Latest | Same model as ingestion, `search_query` input type |
| Vector Search | Qdrant search() API | 1.7+ | Simple, efficient, COSINE distance |
| Python Runtime | Python | 3.9+ | Async support, existing from ingestion |
| Config Management | python-dotenv | Latest | Reuse existing .env file |
| Validation | Custom assertions | N/A | Simple, lightweight, no framework overhead |

---

## Integration with Existing Pipeline

Per implementation plan, `retrieve.py` will:
- **Share environment variables**: Reuse .env file from main.py
- **Share dependencies**: All required packages already in requirements.txt
- **Independent execution**: Can run retrieval tests without re-ingesting
- **Modular design**: Functions can be imported by future FastAPI endpoints

**No new dependencies required** - all packages already installed for ingestion.

---

## Open Questions (None)

All technical decisions resolved. Ready for Phase 1 (data model & contracts).
