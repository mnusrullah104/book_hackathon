# Python Interface Contract: Website URL Embedding Ingestion Pipeline

**Feature**: 002-web-embedding-ingestion
**Date**: 2025-12-24
**Purpose**: Define programmatic interface for backend engineers to integrate ingestion pipeline

## Overview

This pipeline exposes a single-file Python module (`main.py`) with a simple programmatic interface. Engineers can import and use the `main()` function or integrate individual components into FastAPI applications.

## Public Interface

### 1. Main Entry Point

```python
async def main(
    urls: list[str],
    *,
    cohere_api_key: str | None = None,
    qdrant_url: str | None = None,
    qdrant_api_key: str | None = None,
    collection_name: str = "web_documents",
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    embedding_model: str = "embed-english-v3.0",
    embedding_dim: int = 1024,
    batch_size: int = 5,
    max_retries: int = 3,
    skip_duplicates: bool = True,
    verbose: bool = True
) -> IngestionResult:
    """
    Ingest URLs, generate embeddings, and store in Qdrant.

    Args:
        urls: List of website URLs to process
        cohere_api_key: Cohere API key (defaults to COHERE_API_KEY env var)
        qdrant_url: Qdrant instance URL (defaults to QDRANT_URL env var)
        qdrant_api_key: Qdrant API key (defaults to QDRANT_API_KEY env var)
        collection_name: Target Qdrant collection (created if not exists)
        chunk_size: Target tokens per chunk (128-2048)
        chunk_overlap: Overlapping tokens between chunks (0-chunk_size)
        embedding_model: Cohere model identifier
        embedding_dim: Vector dimensions (384, 512, 768, 1024, 1536)
        batch_size: Concurrent URL processing limit (1-10)
        max_retries: Retry attempts for transient failures (0-5)
        skip_duplicates: Skip URLs already in Qdrant (vs. re-ingest)
        verbose: Enable progress bars and detailed logging

    Returns:
        IngestionResult with success/failure counts and error details

    Raises:
        ValueError: Invalid parameter values
        ConfigurationError: Missing or invalid API credentials
        QdrantConnectionError: Cannot connect to Qdrant

    Example:
        >>> result = await main(
        ...     urls=["https://docs.python.org/3/tutorial/"],
        ...     chunk_size=512,
        ...     verbose=True
        ... )
        >>> print(f"Processed {result.success_count} URLs")
    """
```

---

### 2. Result Types

```python
@dataclass
class IngestionResult:
    """Result of ingestion pipeline execution."""

    success_count: int
    """Number of URLs successfully processed and stored."""

    failed_count: int
    """Number of URLs that failed processing."""

    skipped_count: int
    """Number of URLs skipped (duplicates or too-short content)."""

    total_chunks: int
    """Total number of chunks created and stored."""

    execution_time_seconds: float
    """Total pipeline execution time."""

    failed_urls: list[FailedURL]
    """Details of failed URLs for debugging."""

    @property
    def success_rate(self) -> float:
        """Percentage of successfully processed URLs."""
        total = self.success_count + self.failed_count
        return (self.success_count / total * 100) if total > 0 else 0.0


@dataclass
class FailedURL:
    """Details of a failed URL ingestion."""

    url: str
    """The failed URL."""

    error_type: str
    """Error category: 'http_error', 'parse_error', 'embedding_error', 'storage_error'."""

    error_message: str
    """Human-readable error description."""

    timestamp: str
    """ISO 8601 timestamp of failure."""

    retry_count: int
    """Number of retry attempts made."""
```

---

### 3. Exception Types

```python
class IngestionError(Exception):
    """Base exception for all ingestion pipeline errors."""
    pass


class ConfigurationError(IngestionError):
    """Raised when configuration is invalid or incomplete."""
    pass


class QdrantConnectionError(IngestionError):
    """Raised when cannot connect to Qdrant."""
    pass


class CohereAPIError(IngestionError):
    """Raised when Cohere API returns non-transient error."""
    pass
```

---

## Usage Examples

### Example 1: Simple Single URL Ingestion

```python
import asyncio
from backend.main import main

async def ingest_single_url():
    result = await main(
        urls=["https://docs.python.org/3/tutorial/index.html"],
        verbose=True
    )

    print(f"Success: {result.success_count}")
    print(f"Chunks created: {result.total_chunks}")
    print(f"Time: {result.execution_time_seconds:.2f}s")

asyncio.run(ingest_single_url())
```

**Expected Output**:
```
Processing 1 URLs...
[████████████████████████████████] 1/1 URLs processed
Success: 1
Chunks created: 8
Time: 3.45s
```

---

### Example 2: Batch Ingestion with Custom Config

```python
import asyncio
from backend.main import main

async def ingest_documentation():
    urls = [
        "https://docs.python.org/3/tutorial/introduction.html",
        "https://docs.python.org/3/tutorial/controlflow.html",
        "https://docs.python.org/3/tutorial/datastructures.html",
        "https://docs.python.org/3/tutorial/modules.html",
        "https://docs.python.org/3/tutorial/errors.html",
    ]

    result = await main(
        urls=urls,
        chunk_size=1024,        # Larger chunks
        chunk_overlap=100,      # More overlap
        batch_size=3,           # Limit concurrency
        skip_duplicates=True,   # Skip if already ingested
        verbose=True
    )

    print(f"\n=== Ingestion Report ===")
    print(f"Processed: {result.success_count + result.failed_count + result.skipped_count}")
    print(f"Success: {result.success_count} ({result.success_rate:.1f}%)")
    print(f"Failed: {result.failed_count}")
    print(f"Skipped: {result.skipped_count}")
    print(f"Total chunks: {result.total_chunks}")

    if result.failed_urls:
        print(f"\n=== Failed URLs ===")
        for failed in result.failed_urls:
            print(f"- {failed.url}: {failed.error_message}")

asyncio.run(ingest_documentation())
```

**Expected Output**:
```
Processing 5 URLs...
[████████████████████████████████] 5/5 URLs processed

=== Ingestion Report ===
Processed: 5
Success: 5 (100.0%)
Failed: 0
Skipped: 0
Total chunks: 42
```

---

### Example 3: FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from backend.main import main, IngestionResult

app = FastAPI()

class IngestRequest(BaseModel):
    urls: list[HttpUrl]
    chunk_size: int = 512
    skip_duplicates: bool = True

class IngestResponse(BaseModel):
    success_count: int
    failed_count: int
    total_chunks: int
    execution_time_seconds: float
    failed_urls: list[dict]

@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_urls(request: IngestRequest):
    """
    Ingest website URLs and generate embeddings.

    Example request:
    ```json
    {
      "urls": ["https://docs.python.org/3/tutorial/"],
      "chunk_size": 512,
      "skip_duplicates": true
    }
    ```
    """
    try:
        result: IngestionResult = await main(
            urls=[str(url) for url in request.urls],
            chunk_size=request.chunk_size,
            skip_duplicates=request.skip_duplicates,
            verbose=False  # Disable progress bars in API context
        )

        return IngestResponse(
            success_count=result.success_count,
            failed_count=result.failed_count,
            total_chunks=result.total_chunks,
            execution_time_seconds=result.execution_time_seconds,
            failed_urls=[
                {
                    "url": f.url,
                    "error_type": f.error_type,
                    "error_message": f.error_message
                }
                for f in result.failed_urls
            ]
        )
    except ConfigurationError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except QdrantConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Qdrant unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
```

---

### Example 4: Error Handling

```python
import asyncio
from backend.main import main, ConfigurationError, QdrantConnectionError

async def ingest_with_error_handling():
    urls = ["https://example.com", "https://invalid-url"]

    try:
        result = await main(
            urls=urls,
            cohere_api_key="invalid-key-for-testing",
            verbose=True
        )
    except ConfigurationError as e:
        print(f"Config error: {e}")
        return
    except QdrantConnectionError as e:
        print(f"Qdrant error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    # Handle partial failures
    if result.failed_count > 0:
        print(f"Warning: {result.failed_count} URLs failed")
        for failed in result.failed_urls:
            print(f"  - {failed.url}: {failed.error_message}")

    # Success
    print(f"Successfully ingested {result.success_count} URLs")

asyncio.run(ingest_with_error_handling())
```

---

## Configuration via Environment Variables

**Required Environment Variables**:
```bash
export COHERE_API_KEY="your-cohere-api-key"
export QDRANT_URL="https://your-cluster.qdrant.io:6333"
export QDRANT_API_KEY="your-qdrant-api-key"
```

**Optional Environment Variables** (override defaults):
```bash
export CHUNK_SIZE=512
export CHUNK_OVERLAP=50
export EMBEDDING_MODEL="embed-english-v3.0"
export EMBEDDING_DIM=1024
export BATCH_SIZE=5
export MAX_RETRIES=3
export COLLECTION_NAME="web_documents"
```

---

## Validation Rules

### Input Validation

| Parameter | Validation | Error if Violated |
|-----------|-----------|-------------------|
| `urls` | Non-empty list, each valid HTTP/HTTPS URL | ValueError |
| `chunk_size` | 128 ≤ value ≤ 2048 | ValueError |
| `chunk_overlap` | 0 < value < chunk_size | ValueError |
| `embedding_dim` | One of [384, 512, 768, 1024, 1536] | ValueError |
| `batch_size` | 1 ≤ value ≤ 10 | ValueError |
| `max_retries` | 0 ≤ value ≤ 5 | ValueError |
| `cohere_api_key` | Non-empty string (after env var resolution) | ConfigurationError |
| `qdrant_url` | Valid URL (after env var resolution) | ConfigurationError |

### Runtime Validation

- Qdrant connection tested on startup (fail-fast if unreachable)
- Cohere API key validated with test embedding call
- Collection created automatically if not exists (with correct schema)

---

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Single URL fetch | 200-1000ms | Network-dependent |
| Text extraction | 10-50ms | CPU-bound (BeautifulSoup) |
| Chunking (1000 tokens) | 5-10ms | CPU-bound (LangChain) |
| Embedding generation (batch of 96) | 500-2000ms | Cohere API latency |
| Qdrant upsert (batch of 100) | 100-500ms | Network + indexing time |
| **Total per URL (avg)** | 2-5 seconds | Assuming ~10 chunks per URL |

**Batch Processing Efficiency**:
- 5 concurrent URLs: ~10 URLs/minute (limited by Cohere free tier)
- 100 URLs batch: ~10-20 minutes (assuming no rate limit delays)

---

## Testing Interface

```python
# Unit test example
import pytest
from backend.main import main, IngestionResult

@pytest.mark.asyncio
async def test_single_url_ingestion():
    result: IngestionResult = await main(
        urls=["https://example.com"],
        verbose=False
    )

    assert result.success_count == 1
    assert result.failed_count == 0
    assert result.total_chunks > 0
    assert result.execution_time_seconds > 0


@pytest.mark.asyncio
async def test_invalid_url_handling():
    result: IngestionResult = await main(
        urls=["https://invalid-url-12345.com"],
        verbose=False
    )

    assert result.failed_count == 1
    assert len(result.failed_urls) == 1
    assert result.failed_urls[0].error_type == "http_error"


@pytest.mark.asyncio
async def test_duplicate_skipping():
    url = "https://example.com"

    # First ingestion
    result1 = await main(urls=[url], verbose=False)
    assert result1.success_count == 1

    # Second ingestion (should skip)
    result2 = await main(urls=[url], skip_duplicates=True, verbose=False)
    assert result2.skipped_count == 1
    assert result2.success_count == 0
```

---

## Versioning & Compatibility

**Interface Version**: 1.0.0

**Breaking Changes Policy**:
- Function signature changes: Major version bump
- New optional parameters: Minor version bump
- Bug fixes: Patch version bump

**Backwards Compatibility**:
- All parameters have sensible defaults (except required URLs)
- Environment variable fallbacks ensure existing deployments work
- Error types are stable (safe to catch in production code)

---

## Future Enhancements (Out of Scope)

- Streaming results via async generator (for long-running batches)
- Progress callback hooks (custom progress tracking)
- Pluggable chunking strategies (custom splitters)
- Content filtering hooks (e.g., skip pages with specific patterns)
- Metadata enrichment hooks (add custom fields to payload)
