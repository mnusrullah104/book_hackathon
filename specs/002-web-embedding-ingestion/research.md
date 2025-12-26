# Research: Website URL Embedding Ingestion Pipeline

**Feature**: 002-web-embedding-ingestion
**Date**: 2025-12-24
**Purpose**: Resolve technical decisions for web crawling, chunking, embedding, and vector storage

## Research Questions & Decisions

### 1. HTML Parsing & Text Extraction

**Question**: Which HTML parsing approach provides the best balance of text quality and simplicity for web ingestion?

**Decision**: Use BeautifulSoup4 with `html.parser` backend

**Rationale**:
- **BeautifulSoup4** is the de facto standard for HTML parsing in Python with excellent documentation
- `html.parser` backend (Python stdlib) avoids external C dependencies (lxml) for simpler deployment
- Provides robust handling of malformed HTML (common in real-world websites)
- Simple API for tag removal and text extraction: `.get_text()` with separator configuration
- Supports selective tag preservation (keep `<p>`, `<h1-h6>`, `<li>` structure)
- Lightweight and fast enough for batch processing (not CPU-bound, network I/O is bottleneck)

**Alternatives Considered**:
- **lxml**: Faster but requires C dependencies, added deployment complexity
- **html5lib**: Most standards-compliant but 10x slower than html.parser for our use case
- **Scrapy**: Full-featured crawler but overkill for simple URL fetching (we don't need crawl logic, link following, or robots.txt handling)
- **Playwright/Selenium**: Handles JavaScript-rendered content but 100x slower and resource-intensive (not needed for static documentation sites)

**Implementation Notes**:
- Extract title from `<title>` or `<h1>` tags
- Remove `<script>`, `<style>`, `<nav>`, `<footer>`, `<aside>` tags before text extraction
- Preserve paragraph breaks with newline separators
- Handle edge case: if extracted text < 50 chars, log warning and skip URL

---

### 2. Text Chunking Strategy

**Question**: What chunking method balances retrieval quality, embedding efficiency, and semantic coherence?

**Decision**: RecursiveCharacterTextSplitter from LangChain with 512 token chunks and 50-token overlap

**Rationale**:
- **512 tokens** is optimal for Cohere embed-english-v3.0 (supports up to 512 tokens natively)
- **50-token overlap** (10%) prevents semantic boundary loss - ensures retrieval doesn't miss information split across chunks
- **RecursiveCharacterTextSplitter** attempts sentence-boundary splits before character-level splits (preserves semantic units)
- LangChain's splitter is battle-tested and integrates well with tiktoken for accurate token counting
- Configurable via parameters (chunk_size, chunk_overlap) without code changes

**Alternatives Considered**:
- **Fixed character splits**: Naive, breaks mid-sentence/mid-word, poor retrieval quality
- **Sentence-boundary only**: Variable chunk sizes, some very small (<100 tokens), others very large (>1000 tokens), inefficient
- **Semantic chunking (e.g., by topic)**: Requires additional LLM calls, 10x slower, unnecessary for documentation content
- **Larger chunks (1024+ tokens)**: Exceeds Cohere's optimal input size, degrades embedding quality, reduces retrieval granularity

**Implementation Notes**:
- Use `tiktoken` with `cl100k_base` encoding for accurate token counting (GPT-4 tokenizer, widely compatible)
- Store `chunk_index` (position in document) and `token_count` in metadata for debugging
- For very small documents (<512 tokens), create single chunk (no artificial splitting)

---

### 3. Cohere Embedding Model Selection

**Question**: Which Cohere embedding model provides the best retrieval quality for technical documentation?

**Decision**: `embed-english-v3.0` with `search_document` input type

**Rationale**:
- **embed-english-v3.0** is Cohere's latest English embedding model with superior retrieval performance over v2
- **1024 dimensions** (default) balances quality and storage efficiency (alternative: 384, 512, 768, 1536)
- **`search_document` input type** optimizes embeddings for storage (vs. `search_query` for queries, `classification` for labeling)
- Supports batch API calls (up to 96 texts per request) for efficient processing
- Free tier: 100 API calls/month (sufficient for testing, production requires paid plan)

**Alternatives Considered**:
- **embed-multilingual-v3.0**: Supports 100+ languages but 15% lower performance on English-only content
- **embed-english-light-v3.0**: 50% faster, 30% lower quality (not suitable for technical documentation where precision matters)
- **OpenAI text-embedding-3-small**: Comparable quality but per-token pricing more expensive for large documents
- **Sentence-Transformers (open-source)**: Free but requires GPU for acceptable speed, deployment complexity

**Implementation Notes**:
- Use batch API with 96 texts per call to minimize latency (single HTTP request per batch)
- Configure dimension via environment variable `COHERE_EMBEDDING_DIM=1024` (default)
- Handle rate limiting: Cohere free tier limits to 10 requests/min (implement exponential backoff)
- Store model name in metadata for future model migrations

---

### 4. Qdrant Collection Schema

**Question**: How should Qdrant collections be structured for optimal retrieval and metadata filtering?

**Decision**: Single collection `web_documents` with 1024-dimensional vectors and rich metadata payload

**Rationale**:
- **Single collection** simplifies retrieval (no cross-collection search needed) and reduces operational overhead
- **1024 dimensions** matches Cohere embed-english-v3.0 default output
- **COSINE distance metric** for similarity (standard for normalized embeddings, range [0, 2])
- **Payload schema** stores: `url` (source), `title`, `chunk_text`, `chunk_index`, `timestamp`, `token_count`, `chunk_config` (for A/B testing chunking strategies)
- **Indexed fields**: `url` (for deduplication), `timestamp` (for temporal filtering)

**Alternatives Considered**:
- **Multiple collections per domain**: Overcomplicates retrieval, no significant quality benefit
- **DOT product distance**: Slightly faster but assumes normalized vectors (COSINE is more robust)
- **EUCLIDEAN distance**: Not suitable for high-dimensional semantic embeddings (curse of dimensionality)

**Implementation Notes**:
- Initialize collection with `create_collection()` using `VectorParams(size=1024, distance=Distance.COSINE)`
- Use UUID v4 for `point_id` (unique, avoids collisions in distributed scenarios)
- Create payload index for `url` field: `create_payload_index("url", field_schema="keyword")`
- Retention: No TTL (time-to-live) - assume ingested data is permanent unless explicitly deleted

---

### 5. Batch Processing & Parallelization

**Question**: How should batch URL processing be parallelized to maximize throughput while respecting API rate limits?

**Decision**: `asyncio` with semaphore-limited concurrency (5 concurrent requests)

**Rationale**:
- **`asyncio`** enables non-blocking I/O for network requests (10x throughput vs. synchronous processing)
- **Semaphore(5)** limits concurrent requests to avoid rate limit exhaustion (Cohere free tier: 10 req/min)
- **`aiohttp`** for async HTTP requests (replaces `requests` library)
- **`qdrant-client`** supports async operations natively
- Graceful degradation: if one URL fails, others continue processing

**Alternatives Considered**:
- **Threading (`concurrent.futures.ThreadPoolExecutor`)**: GIL contention in Python, lower throughput than asyncio for I/O-bound tasks
- **Multiprocessing**: Overkill for I/O-bound tasks, process overhead > benefit
- **Synchronous processing**: 10x slower, unacceptable for batch ingestion
- **Unlimited concurrency**: Risk of rate limit bans, resource exhaustion (memory, file descriptors)

**Implementation Notes**:
- Use `asyncio.Semaphore(5)` to limit concurrent Cohere API calls
- Implement retry logic with exponential backoff: max 3 retries, base delay 1s, max delay 16s
- Log failed URLs to `failed_urls.json` for manual review
- Track progress with `tqdm` or simple counter (processed/total)

---

### 6. Error Handling & Retry Strategy

**Question**: What retry strategy ensures resilience without wasting time on permanent failures?

**Decision**: Exponential backoff with jitter, max 3 retries for transient errors only

**Rationale**:
- **Transient errors** (429 rate limit, 500 server error, network timeout): Retry with backoff
- **Permanent errors** (401 auth failed, 404 not found, invalid URL): Fail immediately, no retry
- **Exponential backoff**: delay = base_delay * (2 ** attempt) + random_jitter
- **Max 3 retries**: balances resilience and performance (after 3 failures, likely permanent issue)
- **Jitter** (random 0-1s): prevents thundering herd if multiple requests hit rate limit simultaneously

**Alternatives Considered**:
- **Linear backoff**: Slower recovery from rate limits, less efficient
- **Unlimited retries**: Risk of infinite loops on misconfiguration
- **No retries**: Fragile, single network hiccup fails entire batch
- **Circuit breaker pattern**: Overcomplicated for this use case (no long-running service, batch job only)

**Implementation Notes**:
- Use `tenacity` library for decorator-based retry logic
- Configure per-service retries: Cohere (transient only), Qdrant (all errors), HTTP fetch (network only)
- Log retry attempts with delay duration for observability
- Terminal errors: log to `error.log` with full stack trace and URL

---

### 7. Configuration Management

**Question**: How should pipeline parameters be configured without requiring code changes?

**Decision**: Environment variables + optional config file (`.env` + `config.yaml`)

**Rationale**:
- **Environment variables** for secrets (COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY)
- **config.yaml** for operational parameters (chunk_size, overlap, batch_size, retry_limit, concurrency)
- **`pydantic` BaseSettings** for validation and type coercion
- Follows 12-factor app principles (config separate from code)
- Easy integration with Docker, cloud platforms (env var injection)

**Alternatives Considered**:
- **Command-line arguments only**: Tedious for many parameters, no secret management
- **Hardcoded constants**: Requires code changes for tuning, violates 12-factor
- **Database config**: Overkill for batch script, adds unnecessary dependency
- **JSON config**: Less human-friendly than YAML, no comment support

**Implementation Notes**:
- Use `python-dotenv` to load `.env` file
- Pydantic model validates required fields on startup (fail-fast)
- Provide `config.example.yaml` with recommended defaults
- Support env var override: `CHUNK_SIZE=1024` overrides `config.yaml` value

---

## Summary of Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| HTML Parsing | BeautifulSoup4 | 4.12+ | Robust, simple, handles malformed HTML |
| Text Chunking | LangChain RecursiveCharacterTextSplitter | 0.1+ | Semantic-aware, configurable, battle-tested |
| Token Counting | tiktoken | 0.5+ | Accurate, GPT-4 tokenizer |
| Embeddings | Cohere embed-english-v3.0 | Latest | SOTA quality, batch API, 1024-dim |
| Vector DB | Qdrant Cloud | 1.7+ | Free tier, fast, rich metadata support |
| HTTP Client | aiohttp | 3.9+ | Async, efficient for batch requests |
| Async Runtime | asyncio | stdlib | Non-blocking I/O, native Python |
| Retry Logic | tenacity | 8.2+ | Decorator-based, exponential backoff |
| Config Management | pydantic + python-dotenv | 2.0+ | Type-safe, env var support |
| Progress Tracking | tqdm | 4.66+ | User-friendly progress bars |

---

## Integration with UV Package Manager

Per user requirements, project uses **UV** (ultra-fast Python package manager):

**Setup Commands**:
```bash
# Initialize project
uv init

# Install dependencies
uv pip install beautifulsoup4 aiohttp cohere qdrant-client langchain tiktoken tenacity pydantic python-dotenv tqdm

# Generate requirements.txt
uv pip freeze > requirements.txt
```

**Benefits of UV**:
- 10-100x faster than pip for dependency resolution
- Deterministic installs (lockfile support)
- Compatible with existing pip ecosystem
- No breaking changes to project structure

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Cohere rate limits exceeded | High | Medium | Semaphore limiting, exponential backoff |
| Large batch OOM (out of memory) | Medium | High | Process in smaller batches (100 URLs max) |
| Malformed HTML breaks parser | Medium | Low | BeautifulSoup handles gracefully, log warnings |
| Qdrant connection failure mid-batch | Low | High | Retry logic, checkpoint progress |
| Embedding dimension mismatch | Low | Critical | Validation on startup, fail-fast |

---

## Open Questions (None)

All technical decisions resolved. Ready for Phase 1 (data model & contracts).
