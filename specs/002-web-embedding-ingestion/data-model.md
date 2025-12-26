# Data Model: Website URL Embedding Ingestion Pipeline

**Feature**: 002-web-embedding-ingestion
**Date**: 2025-12-24
**Purpose**: Define data structures for web document ingestion, chunking, embedding, and storage

## Overview

This system processes website URLs through a pipeline: fetch → extract → chunk → embed → store. Data flows through five core entities, culminating in storage in Qdrant vector database.

## Entity Definitions

### 1. IngestionConfig

**Purpose**: Configuration parameters for the ingestion pipeline

**Attributes**:
- `chunk_size` (int): Target token count per chunk (default: 512)
- `chunk_overlap` (int): Overlapping tokens between chunks (default: 50)
- `embedding_model` (str): Cohere model identifier (default: "embed-english-v3.0")
- `embedding_dim` (int): Vector dimensions (default: 1024)
- `batch_size` (int): URLs processed concurrently (default: 5)
- `max_retries` (int): Retry attempts for transient failures (default: 3)
- `retry_base_delay` (float): Base delay in seconds for exponential backoff (default: 1.0)

**Validation Rules**:
- `chunk_size` must be between 128 and 2048
- `chunk_overlap` must be less than `chunk_size` and greater than 0
- `embedding_dim` must be one of [384, 512, 768, 1024, 1536]
- `batch_size` must be between 1 and 10 (rate limit protection)
- `max_retries` must be between 0 and 5

**Lifecycle**: Created once at pipeline initialization, immutable during execution

---

### 2. WebDocument

**Purpose**: Represents a fetched website page before processing

**Attributes**:
- `url` (str): Original source URL (unique identifier)
- `title` (str | None): Extracted from `<title>` or `<h1>` tag
- `raw_html` (str): Original HTML content as fetched
- `extracted_text` (str): Cleaned text after HTML tag removal
- `fetch_timestamp` (datetime): ISO 8601 timestamp of fetch operation
- `content_type` (str): HTTP Content-Type header value (e.g., "text/html; charset=utf-8")
- `status_code` (int): HTTP response status (200, 404, 500, etc.)
- `text_length` (int): Character count of `extracted_text`

**Relationships**:
- One WebDocument → Many TextChunks (1:N, after chunking)

**Validation Rules**:
- `url` must be valid HTTP/HTTPS URL
- `status_code` must be 200 for successful processing (others logged as failures)
- `text_length` must be ≥ 50 characters (too-short content triggers warning)
- `extracted_text` must not be empty string (empty triggers skip)

**Lifecycle**: Created after successful HTTP fetch, discarded after chunking completes (not persisted to database)

---

### 3. TextChunk

**Purpose**: Represents a segmented portion of a web document

**Attributes**:
- `chunk_id` (UUID): Unique identifier (UUID v4)
- `source_url` (str): Parent WebDocument URL
- `chunk_text` (str): Actual text content of this chunk
- `chunk_index` (int): Zero-based position in parent document (0, 1, 2, ...)
- `token_count` (int): Exact token count using tiktoken
- `chunking_config` (dict): Snapshot of IngestionConfig used (for reproducibility)
- `created_at` (datetime): ISO 8601 timestamp of chunk creation

**Relationships**:
- Many TextChunks → One WebDocument (N:1, source reference)
- One TextChunk → One Embedding (1:1, after embedding generation)

**Validation Rules**:
- `chunk_text` must not be empty
- `token_count` must match actual tokenization (validation check)
- `chunk_index` must be non-negative
- `chunking_config` must contain keys: `chunk_size`, `chunk_overlap`

**Lifecycle**: Created during chunking phase, persisted in Qdrant payload (metadata)

---

### 4. Embedding

**Purpose**: Vector representation of a text chunk

**Attributes**:
- `embedding_vector` (List[float]): Numerical representation from Cohere (length = `embedding_dim`)
- `dimension` (int): Vector size (typically 1024)
- `model_name` (str): Cohere model identifier (e.g., "embed-english-v3.0")
- `generation_timestamp` (datetime): ISO 8601 timestamp of embedding creation
- `input_type` (str): Cohere input type used (e.g., "search_document")

**Relationships**:
- One Embedding → One TextChunk (1:1, embedded content)

**Validation Rules**:
- `embedding_vector` length must equal `dimension`
- All vector values must be floats (no NaN, Inf)
- `dimension` must match Qdrant collection configuration

**Lifecycle**: Created after Cohere API call, immediately stored in Qdrant (not persisted elsewhere)

---

### 5. QdrantPoint

**Purpose**: Complete storage entity in Qdrant vector database

**Attributes**:
- `id` (UUID): Qdrant point ID (same as TextChunk.chunk_id)
- `vector` (List[float]): Embedding vector (from Embedding.embedding_vector)
- `payload` (dict): Metadata dictionary containing:
  - `url` (str): Source URL
  - `title` (str | None): Document title
  - `chunk_text` (str): Full text of chunk
  - `chunk_index` (int): Position in document
  - `timestamp` (str): ISO 8601 ingestion time
  - `token_count` (int): Token count
  - `chunk_config` (dict): Chunking parameters used
  - `model_name` (str): Embedding model identifier
  - `dimension` (int): Vector dimensions

**Relationships**:
- Stored in Qdrant collection: `web_documents`
- No foreign keys (self-contained document)

**Validation Rules**:
- `id` must be unique within collection
- `vector` length must match collection vector size (1024)
- `payload.url` must be indexed for deduplication queries

**Lifecycle**: Created during Qdrant upsert operation, persists until explicitly deleted

---

## Data Flow Diagram

```
┌─────────────────┐
│  Input: URLs    │
│  (List[str])    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WebDocument    │ Fetch HTML via aiohttp
│  (raw + clean)  │ Extract text with BeautifulSoup
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TextChunk[]    │ Chunk text with LangChain
│  (segmented)    │ RecursiveCharacterTextSplitter
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Embedding[]    │ Generate vectors with Cohere
│  (vectors)      │ embed-english-v3.0 batch API
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  QdrantPoint[]  │ Upsert to Qdrant collection
│  (stored)       │ web_documents (COSINE distance)
└─────────────────┘
```

## Qdrant Collection Schema

**Collection Name**: `web_documents`

**Configuration**:
```python
{
  "vectors": {
    "size": 1024,           # Match Cohere embed-english-v3.0 default
    "distance": "Cosine"    # Standard for normalized embeddings
  },
  "optimizers_config": {
    "default_segment_number": 2  # Balance indexing speed and memory
  },
  "hnsw_config": {
    "m": 16,                # Connections per layer (default: 16)
    "ef_construct": 100     # Construction time accuracy (default: 100)
  }
}
```

**Payload Indexes**:
```python
# Index for deduplication queries
create_payload_index("url", field_schema="keyword")

# Index for temporal filtering (optional)
create_payload_index("timestamp", field_schema="datetime")
```

**Storage Estimate**:
- Vector: 1024 floats × 4 bytes = 4KB per point
- Payload: ~2KB avg (URL + text + metadata)
- Total: ~6KB per chunk
- 100,000 chunks = 600MB (well within free tier limits)

---

## Deduplication Strategy

**Problem**: Same URL ingested multiple times → duplicate embeddings

**Solution**: Pre-ingestion check using Qdrant scroll API

**Process**:
1. Before ingesting URL, query Qdrant: `scroll(filter={"must": [{"key": "url", "match": {"value": url}}]})`
2. If results found, options:
   - **Skip**: Log "URL already ingested" and continue to next URL
   - **Update**: Delete existing points and re-ingest (if content changed)
   - **Version**: Add `version` field to payload, keep historical versions

**Chosen Approach**: Skip (simplest, MVP-appropriate)

---

## Error States & Handling

| Entity | Error State | Handling |
|--------|------------|----------|
| WebDocument | `status_code != 200` | Log error, skip chunking, mark as failed |
| WebDocument | `text_length < 50` | Log warning, skip chunking, mark as too-short |
| TextChunk | Empty `chunk_text` | Should never occur (validation prevents), log critical error |
| Embedding | Cohere API failure | Retry with exponential backoff (max 3 attempts), then skip |
| QdrantPoint | Upsert failure | Retry with backoff, log error if persistent |

---

## Future Extensions (Out of Scope for MVP)

- **Incremental updates**: Track `last_modified` header, re-ingest only if changed
- **Versioning**: Store multiple versions of same URL with `version` field
- **Content hashing**: Use SHA-256 hash for exact deduplication (vs. URL-based)
- **Metadata enrichment**: Add domain, author, language detection
- **Expiration**: TTL for outdated content (e.g., delete after 6 months)

---

## Validation Checklist

- [x] All entities have clear purpose and lifecycle
- [x] Relationships are explicit (1:1, 1:N)
- [x] Validation rules are testable
- [x] Qdrant schema matches embedding dimensions
- [x] Deduplication strategy defined
- [x] Error states documented
- [x] Storage estimates provided
