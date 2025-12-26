# Feature Specification: Website URL Embedding Ingestion Pipeline

**Feature Branch**: `002-web-embedding-ingestion`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "Deploy website URLs, generate embeddings, and store them in a vector database for a RAG chatbot. Target audience: Backend engineers building a production-ready RAG pipeline. Focus: Reliable ingestion, embedding generation using Cohere, and storage in Qdrant"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single URL Content Ingestion (Priority: P1)

As a backend engineer, I want to ingest content from a single website URL so that I can quickly test the pipeline and verify embeddings are generated and stored correctly.

**Why this priority**: This is the foundational capability. Without being able to ingest a single URL successfully, bulk ingestion is not possible. This serves as the MVP that validates the entire pipeline end-to-end.

**Independent Test**: Provide a single URL (e.g., https://docs.python.org/3/tutorial/index.html), execute the ingestion pipeline, and verify that:
- Content is extracted and cleaned
- Embeddings are generated via Cohere
- Data is stored in Qdrant with queryable metadata
- The ingested content can be retrieved via Qdrant search

**Acceptance Scenarios**:

1. **Given** a valid website URL, **When** the ingestion pipeline processes it, **Then** the system extracts text content, generates embeddings, and stores them in Qdrant with metadata (URL, title, timestamp)
2. **Given** a URL with HTML content, **When** text extraction occurs, **Then** the system removes HTML tags, scripts, and styling while preserving meaningful text structure
3. **Given** embeddings are generated, **When** querying Qdrant for similar content, **Then** the ingested content is retrievable with similarity scores

---

### User Story 2 - Bulk URL Batch Processing (Priority: P2)

As a backend engineer, I want to ingest multiple website URLs in a single batch so that I can efficiently populate the vector database with a complete knowledge base.

**Why this priority**: After validating single URL ingestion, bulk processing is essential for production use. This enables efficient scaling to real-world scenarios where hundreds or thousands of URLs need processing.

**Independent Test**: Provide a list of 10 URLs, execute batch ingestion, and verify:
- All URLs are processed successfully
- Failed URLs are logged with error details
- Processing is parallelized for efficiency
- Progress tracking is available

**Acceptance Scenarios**:

1. **Given** a list of 10 valid URLs, **When** batch ingestion runs, **Then** all URLs are processed and stored in Qdrant within a reasonable time (proportional to content size)
2. **Given** a batch with 3 invalid URLs and 7 valid URLs, **When** batch processing occurs, **Then** 7 URLs succeed, 3 are logged as failures, and the pipeline continues without stopping
3. **Given** a batch ingestion is running, **When** queried for progress, **Then** the system reports number of URLs processed, pending, and failed

---

### User Story 3 - Configurable Chunking Strategy (Priority: P2)

As a backend engineer, I want to configure how content is chunked before embedding generation so that I can optimize retrieval quality for different content types (long articles, documentation, FAQs).

**Why this priority**: Chunking strategy significantly impacts RAG retrieval quality. Different content types benefit from different chunk sizes. This flexibility is critical for production deployments.

**Independent Test**: Configure different chunk sizes (512, 1024, 2048 tokens) and overlap settings, run ingestion on the same URL, and verify:
- Content is chunked according to specified parameters
- Each chunk is embedded separately
- Metadata includes chunk index and position information

**Acceptance Scenarios**:

1. **Given** a configuration with chunk_size=512 and overlap=50, **When** processing a 2000-token document, **Then** the system creates approximately 4 overlapping chunks stored as separate Qdrant entries
2. **Given** different chunking configurations, **When** the same URL is ingested twice with different settings, **Then** both versions coexist in Qdrant with configuration metadata distinguishing them
3. **Given** a chunk boundary falls mid-sentence, **When** chunking occurs, **Then** the system preserves sentence boundaries when possible (semantic chunking)

---

### User Story 4 - Error Handling and Retry Logic (Priority: P3)

As a backend engineer, I want automatic retry logic for transient failures so that the ingestion pipeline is resilient to network issues, rate limits, and temporary service outages.

**Why this priority**: Production systems must handle transient failures gracefully. While not blocking the MVP, this capability significantly improves operational reliability.

**Independent Test**: Simulate Cohere API rate limiting and network failures, run ingestion, and verify:
- Failed requests are retried with exponential backoff
- Persistent failures are logged and skipped
- Pipeline completes successfully for non-failing URLs

**Acceptance Scenarios**:

1. **Given** the Cohere API returns a 429 rate limit error, **When** the pipeline encounters this, **Then** the system waits with exponential backoff and retries up to 3 times
2. **Given** a network timeout occurs during URL crawling, **When** processing that URL, **Then** the system retries the request and logs a warning if retries are exhausted
3. **Given** a persistent failure (invalid API key), **When** multiple retries fail, **Then** the system logs the error, marks the batch as failed, and provides actionable error messages

---

### Edge Cases

- **Empty or minimal content**: What happens when a URL returns a page with no meaningful text (e.g., only navigation elements)?
- **Large documents**: How does the system handle extremely large documents (10MB+ HTML pages)?
- **Duplicate URLs**: What happens when the same URL is ingested multiple times?
- **Unsupported content types**: How does the system handle PDFs, images, or non-HTML content?
- **Malformed HTML**: How does the parser handle broken or non-standard HTML?
- **Authentication-required pages**: How does the system handle URLs behind login walls?
- **Rate limiting**: How does the system handle Cohere API rate limits during batch processing?
- **Connection failures**: What happens if Qdrant is unreachable during ingestion?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a single website URL and extract text content from the HTML page
- **FR-002**: System MUST clean extracted text by removing HTML tags, scripts, CSS, and non-textual elements
- **FR-003**: System MUST chunk extracted text into configurable segments (default: 512 tokens with 50-token overlap)
- **FR-004**: System MUST generate embeddings for each text chunk using Cohere embedding models (embed-english-v3.0 or embed-multilingual-v3.0)
- **FR-005**: System MUST store embeddings in Qdrant with associated metadata (URL, title, chunk_index, timestamp, chunk_size_config)
- **FR-006**: System MUST support batch processing of multiple URLs provided as a list
- **FR-007**: System MUST handle failed URL processing gracefully by logging errors and continuing with remaining URLs
- **FR-008**: System MUST provide configurable parameters for chunking strategy (chunk_size, overlap, chunking_method)
- **FR-009**: System MUST preserve text structure and readability during extraction (paragraphs, headings, lists)
- **FR-010**: System MUST validate URLs before processing (protocol, reachability, content-type)
- **FR-011**: System MUST implement retry logic with exponential backoff for transient API failures (Cohere, Qdrant)
- **FR-012**: System MUST log all ingestion operations (start time, end time, URL, success/failure, error details)
- **FR-013**: System MUST expose ingestion functionality via a programmatic interface compatible with FastAPI integration
- **FR-014**: System MUST deduplicate content based on URL to prevent redundant embedding generation
- **FR-015**: System MUST provide progress tracking for batch ingestion operations (total, processed, pending, failed)

### Key Entities *(include if feature involves data)*

- **WebDocument**: Represents a crawled website page with attributes: URL (source), title (extracted from HTML), raw_html (original content), extracted_text (cleaned text), fetch_timestamp, content_type, status_code
- **TextChunk**: Represents a segment of processed text with attributes: chunk_id (unique identifier), source_url (parent document), chunk_text (actual content), chunk_index (position in document), token_count, chunking_config (parameters used)
- **Embedding**: Represents a vector embedding with attributes: embedding_vector (numerical representation), dimension (vector size, typically 1024 or 1536 for Cohere), model_name (Cohere model used), generation_timestamp
- **IngestionJob**: Represents a batch processing task with attributes: job_id (unique identifier), urls (list of target URLs), status (pending/running/completed/failed), progress_stats (counts of processed/pending/failed), start_time, end_time, configuration (chunking and embedding settings)
- **QdrantEntry**: Represents stored data in vector database with attributes: point_id (Qdrant unique ID), vector (embedding), payload (metadata including URL, title, chunk_index, timestamp, config), collection_name

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Engineers can successfully ingest a single URL and retrieve its content via Qdrant similarity search within 5 seconds
- **SC-002**: System processes batches of 100 URLs with 95%+ success rate (excluding intentionally broken URLs)
- **SC-003**: Embedding generation completes within 2 seconds per chunk on average (dependent on Cohere API latency)
- **SC-004**: Ingested content is immediately queryable in Qdrant (zero-delay availability after ingestion completes)
- **SC-005**: System handles transient failures (network issues, rate limits) without manual intervention in 90%+ of cases
- **SC-006**: Documentation enables a backend engineer to integrate the pipeline into a FastAPI application within 30 minutes
- **SC-007**: Pipeline configuration changes (chunk size, overlap) can be applied without code modifications (config-driven)
- **SC-008**: System logs provide sufficient detail to debug failures without requiring code inspection

## Assumptions

- Cohere API credentials (API key) are provided via environment variables
- Qdrant instance is accessible and properly configured with appropriate collections
- Target websites are publicly accessible (no authentication required) for MVP
- Content is primarily in English (though Cohere supports multilingual, initial focus is English)
- Engineers integrating this pipeline have basic Python knowledge and FastAPI familiarity
- Qdrant collections are pre-initialized with appropriate vector dimensions matching Cohere model output
- Network connectivity is generally stable (transient failures are handled, but persistent network outages are out of scope)
- Target websites serve HTML content (not PDFs, images, or other binary formats in MVP)

## Dependencies

- **Cohere API**: External service for embedding generation - requires valid API key and active subscription
- **Qdrant**: Vector database for storage and retrieval - requires running instance (cloud or self-hosted)
- **Python libraries**: beautifulsoup4 (HTML parsing), requests (HTTP), cohere (SDK), qdrant-client (vector DB interaction)
- **FastAPI ecosystem**: While not directly dependent, pipeline must be designed for easy FastAPI integration

## Constraints

- **Language**: Python 3.9+ required for type hints and async support
- **Framework compatibility**: Must integrate cleanly with FastAPI (async-compatible, no blocking operations)
- **Embedding provider**: Cohere only (not OpenAI, Hugging Face, or other providers)
- **Vector database**: Qdrant only (not Pinecone, Weaviate, or Milvus)
- **Output structure**: Modular design with clear separation of concerns (crawling, chunking, embedding, storage)
- **Testing**: Pipeline components must be independently testable (unit tests for each module)
- **Configuration**: All parameters (chunk size, overlap, model selection, retry limits) must be externally configurable
- **No UI**: Pure backend pipeline with programmatic interface only

## Out of Scope

- **Retrieval logic**: Querying Qdrant for relevant chunks during RAG retrieval is not included
- **Ranking and reranking**: Post-retrieval relevance scoring is not included
- **LLM integration**: Generating responses using retrieved content is not included
- **Frontend or API endpoints**: No web interface or REST API endpoints are provided (engineers integrate programmatically)
- **Evaluation metrics**: Measuring embedding quality, retrieval accuracy, or RAG performance is not included
- **Authentication handling**: Crawling password-protected or login-required pages is not supported
- **Advanced content types**: PDFs, images, videos, or structured data (JSON, XML) are not supported in MVP
- **Incremental updates**: Re-ingesting URLs to detect and update changed content is not included
- **Distributed processing**: Multi-machine or cloud-native batch processing is not included (single-machine execution only)
- **Cost optimization**: Monitoring or minimizing Cohere API usage costs is not included
