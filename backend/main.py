"""
Website URL Embedding Ingestion Pipeline

Production-ready pipeline for ingesting website URLs, generating semantic embeddings
using Cohere API, and storing them in Qdrant vector database for RAG applications.
"""

import os
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import time

# HTTP and HTML parsing
import aiohttp
from bs4 import BeautifulSoup

# Embeddings and chunking
import cohere
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# Vector database
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams

# Utilities
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from tqdm import tqdm


# =============================================================================
# CONFIGURATION & DATA CLASSES
# =============================================================================

@dataclass
class IngestionConfig:
    """Configuration parameters for the ingestion pipeline."""

    chunk_size: int = 512
    chunk_overlap: int = 50
    embedding_model: str = "embed-english-v3.0"
    embedding_dim: int = 1024
    batch_size: int = 5
    max_retries: int = 3
    retry_base_delay: float = 1.0
    collection_name: str = "web_documents"
    timeout: int = 30

    def __post_init__(self):
        """Validate configuration parameters."""
        validate_config(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            embedding_dim=self.embedding_dim,
            batch_size=self.batch_size,
            max_retries=self.max_retries
        )


@dataclass
class FailedURL:
    """Details of a failed URL ingestion."""

    url: str
    error_type: str  # 'http_error', 'parse_error', 'embedding_error', 'storage_error'
    error_message: str
    timestamp: str
    retry_count: int = 0


@dataclass
class IngestionResult:
    """Result of ingestion pipeline execution."""

    success_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    total_chunks: int = 0
    execution_time_seconds: float = 0.0
    failed_urls: List[FailedURL] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Percentage of successfully processed URLs."""
        total = self.success_count + self.failed_count
        return (self.success_count / total * 100) if total > 0 else 0.0


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

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


# =============================================================================
# CONFIGURATION & VALIDATION
# =============================================================================

def load_config(
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
    **kwargs
) -> tuple:
    """
    Load configuration from environment variables with fallbacks.

    Args:
        cohere_api_key: Cohere API key (overrides env var)
        qdrant_url: Qdrant instance URL (overrides env var)
        qdrant_api_key: Qdrant API key (overrides env var)
        **kwargs: Additional configuration parameters

    Returns:
        Tuple of (cohere_api_key, qdrant_url, qdrant_api_key, config)

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

    # Build configuration with env var defaults
    config_dict = {
        "chunk_size": int(os.getenv("CHUNK_SIZE", kwargs.get("chunk_size", 512))),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", kwargs.get("chunk_overlap", 50))),
        "embedding_model": os.getenv("EMBEDDING_MODEL", kwargs.get("embedding_model", "embed-english-v3.0")),
        "embedding_dim": int(os.getenv("EMBEDDING_DIM", kwargs.get("embedding_dim", 1024))),
        "batch_size": int(os.getenv("BATCH_SIZE", kwargs.get("batch_size", 5))),
        "max_retries": int(os.getenv("MAX_RETRIES", kwargs.get("max_retries", 3))),
        "collection_name": os.getenv("COLLECTION_NAME", kwargs.get("collection_name", "web_documents")),
    }

    config = IngestionConfig(**config_dict)

    return cohere_key, qdrant_url_val, qdrant_key, config


def validate_config(
    chunk_size: int,
    chunk_overlap: int,
    embedding_dim: int,
    batch_size: int,
    max_retries: int
):
    """
    Validate configuration parameters.

    Args:
        chunk_size: Target tokens per chunk
        chunk_overlap: Overlapping tokens between chunks
        embedding_dim: Vector dimensions
        batch_size: Concurrent URL processing limit
        max_retries: Retry attempts for transient failures

    Raises:
        ValueError: If any parameter is invalid
    """
    if not 128 <= chunk_size <= 2048:
        raise ValueError(f"chunk_size must be between 128 and 2048, got {chunk_size}")

    if not 0 < chunk_overlap < chunk_size:
        raise ValueError(f"chunk_overlap must be between 0 and {chunk_size}, got {chunk_overlap}")

    if embedding_dim not in [384, 512, 768, 1024, 1536]:
        raise ValueError(f"embedding_dim must be one of [384, 512, 768, 1024, 1536], got {embedding_dim}")

    if not 1 <= batch_size <= 10:
        raise ValueError(f"batch_size must be between 1 and 10, got {batch_size}")

    if not 0 <= max_retries <= 5:
        raise ValueError(f"max_retries must be between 0 and 5, got {max_retries}")


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

def setup_logging(verbose: bool = True):
    """
    Configure structured logging for the pipeline.

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
# PHASE 3: USER STORY 1 - CORE PIPELINE FUNCTIONS
# =============================================================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Retry {retry_state.attempt_number}/3 for URL fetch after {retry_state.outcome.exception()}"
    )
)
async def fetch_url(url: str, session: aiohttp.ClientSession, timeout: int = 30) -> tuple:
    """
    Fetch HTML content from a URL using aiohttp with retry logic.

    Args:
        url: Website URL to fetch
        session: aiohttp ClientSession for connection pooling
        timeout: Request timeout in seconds

    Returns:
        Tuple of (url, html_content, status_code, content_type)

    Raises:
        aiohttp.ClientError: On network failures (after retries)
    """
    logger.info(f"Fetching URL: {url}")
    timeout_obj = aiohttp.ClientTimeout(total=timeout)

    async with session.get(url, timeout=timeout_obj) as response:
        status = response.status
        content_type = response.headers.get('Content-Type', '')
        html = await response.text()

        logger.info(f"Fetched {url}: status={status}, content_type={content_type}, size={len(html)}")
        return url, html, status, content_type


def extract_text(html: str) -> str:
    """
    Extract clean text from HTML using BeautifulSoup.

    Removes script, style, nav, footer, and aside tags while preserving
    paragraph structure.

    Args:
        html: Raw HTML content

    Returns:
        Cleaned text content with preserved structure
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove unwanted tags
    for tag in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
        tag.decompose()

    # Extract text with newline separators
    text = soup.get_text(separator='\n', strip=True)

    # Clean up excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clean_text = '\n'.join(lines)

    logger.debug(f"Extracted {len(clean_text)} characters from HTML")
    return clean_text


def extract_title(html: str) -> Optional[str]:
    """
    Extract title from HTML <title> or <h1> tags.

    Args:
        html: Raw HTML content

    Returns:
        Title string or None if not found
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Try <title> tag first
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        return title_tag.string.strip()

    # Fallback to first <h1> tag
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text(strip=True)

    return None


def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[dict]:
    """
    Chunk text using LangChain RecursiveCharacterTextSplitter.

    Args:
        text: Text content to chunk
        chunk_size: Target tokens per chunk
        chunk_overlap: Overlapping tokens between chunks

    Returns:
        List of chunk dictionaries with text, index, and token count
    """
    # Initialize tokenizer
    encoding = tiktoken.get_encoding("cl100k_base")

    # Create text splitter
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    # Split text
    chunks_text = splitter.split_text(text)

    # Build chunk objects with metadata
    chunks = []
    for idx, chunk_text in enumerate(chunks_text):
        token_count = len(encoding.encode(chunk_text))
        chunks.append({
            "text": chunk_text,
            "index": idx,
            "token_count": token_count
        })

    logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")
    return chunks


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Retry {retry_state.attempt_number}/3 for embedding generation"
    )
)
async def generate_embeddings(
    texts: List[str],
    cohere_client: cohere.AsyncClient,
    model: str = "embed-english-v3.0",
    input_type: str = "search_document"
) -> List[List[float]]:
    """
    Generate embeddings using Cohere batch API with retry logic.

    Args:
        texts: List of text chunks to embed
        cohere_client: Cohere async client
        model: Cohere model identifier
        input_type: Input type for optimization (search_document/search_query)

    Returns:
        List of embedding vectors (list of floats)

    Raises:
        CohereAPIError: On non-transient API errors (after retries)
    """
    logger.info(f"Generating embeddings for {len(texts)} chunks using {model}")

    try:
        response = await cohere_client.embed(
            texts=texts,
            model=model,
            input_type=input_type
        )
        embeddings = response.embeddings
        logger.info(f"Generated {len(embeddings)} embeddings, dim={len(embeddings[0])}")
        return embeddings

    except Exception as e:
        logger.error(f"Cohere API error: {e}")
        raise CohereAPIError(f"Failed to generate embeddings: {e}")


def initialize_qdrant(
    client: QdrantClient,
    collection_name: str,
    vector_size: int = 1024
):
    """
    Create Qdrant collection if it doesn't exist.

    Args:
        client: QdrantClient instance
        collection_name: Name of collection to create
        vector_size: Embedding vector dimensions

    Raises:
        QdrantConnectionError: On connection failures
    """
    try:
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]

        if collection_name in collection_names:
            logger.info(f"Collection '{collection_name}' already exists")
            return

        # Create collection with COSINE distance
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        # Create payload index for URL deduplication
        client.create_payload_index(
            collection_name=collection_name,
            field_name="url",
            field_schema="keyword"
        )

        logger.info(f"Created collection '{collection_name}' with {vector_size}-dim COSINE vectors")

    except Exception as e:
        logger.error(f"Qdrant connection error: {e}")
        raise QdrantConnectionError(f"Failed to initialize Qdrant collection: {e}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Retry {retry_state.attempt_number}/3 for Qdrant storage"
    )
)
async def store_in_qdrant(
    client: QdrantClient,
    collection_name: str,
    url: str,
    title: Optional[str],
    chunks: List[dict],
    embeddings: List[List[float]],
    config: IngestionConfig
):
    """
    Store embeddings and metadata in Qdrant with retry logic.

    Args:
        client: QdrantClient instance
        collection_name: Target collection name
        url: Source URL
        title: Document title
        chunks: List of chunk dictionaries
        embeddings: List of embedding vectors
        config: Ingestion configuration

    Raises:
        QdrantConnectionError: On storage failures (after retries)
    """
    logger.info(f"Storing {len(chunks)} chunks in Qdrant collection '{collection_name}'")

    try:
        points = []
        timestamp = datetime.now().isoformat()

        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid4())
            point = models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "url": url,
                    "title": title,
                    "chunk_text": chunk["text"],
                    "chunk_index": chunk["index"],
                    "token_count": chunk["token_count"],
                    "timestamp": timestamp,
                    "chunk_config": {
                        "chunk_size": config.chunk_size,
                        "chunk_overlap": config.chunk_overlap
                    },
                    "model_name": config.embedding_model,
                    "dimension": config.embedding_dim
                }
            )
            points.append(point)

        # Upsert points to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points
        )

        logger.info(f"Successfully stored {len(points)} points for URL: {url}")

    except Exception as e:
        logger.error(f"Qdrant storage error: {e}")
        raise QdrantConnectionError(f"Failed to store embeddings: {e}")


async def process_single_url(
    url: str,
    session: aiohttp.ClientSession,
    cohere_client: cohere.AsyncClient,
    qdrant_client: QdrantClient,
    config: IngestionConfig
) -> tuple:
    """
    Process a single URL through the full pipeline.

    Pipeline: fetch → extract → chunk → embed → store

    Args:
        url: Website URL to process
        session: aiohttp ClientSession
        cohere_client: Cohere async client
        qdrant_client: Qdrant client
        config: Ingestion configuration

    Returns:
        Tuple of (success: bool, chunks_count: int, error: Optional[FailedURL])
    """
    try:
        # Stage 1: Fetch HTML
        url_str, html, status, content_type = await fetch_url(url, session, config.timeout)

        if status != 200:
            error = FailedURL(
                url=url,
                error_type="http_error",
                error_message=f"HTTP {status}",
                timestamp=datetime.now().isoformat()
            )
            return False, 0, error

        # Stage 2: Extract text and title
        text = extract_text(html)
        title = extract_title(html)

        if len(text) < 50:
            error = FailedURL(
                url=url,
                error_type="parse_error",
                error_message=f"Text too short: {len(text)} chars",
                timestamp=datetime.now().isoformat()
            )
            return False, 0, error

        logger.info(f"Extracted {len(text)} chars from {url}, title='{title}'")

        # Stage 3: Chunk text
        chunks = chunk_text(text, config.chunk_size, config.chunk_overlap)

        # Stage 4: Generate embeddings
        chunk_texts = [c["text"] for c in chunks]
        embeddings = await generate_embeddings(
            chunk_texts,
            cohere_client,
            config.embedding_model
        )

        # Stage 5: Store in Qdrant
        await store_in_qdrant(
            qdrant_client,
            config.collection_name,
            url,
            title,
            chunks,
            embeddings,
            config
        )

        logger.info(f"✓ Successfully processed {url}: {len(chunks)} chunks")
        return True, len(chunks), None

    except aiohttp.ClientError as e:
        error = FailedURL(
            url=url,
            error_type="http_error",
            error_message=str(e),
            timestamp=datetime.now().isoformat()
        )
        logger.error(f"✗ Failed to fetch {url}: {e}")
        return False, 0, error

    except CohereAPIError as e:
        error = FailedURL(
            url=url,
            error_type="embedding_error",
            error_message=str(e),
            timestamp=datetime.now().isoformat()
        )
        logger.error(f"✗ Failed to embed {url}: {e}")
        return False, 0, error

    except QdrantConnectionError as e:
        error = FailedURL(
            url=url,
            error_type="storage_error",
            error_message=str(e),
            timestamp=datetime.now().isoformat()
        )
        logger.error(f"✗ Failed to store {url}: {e}")
        return False, 0, error

    except Exception as e:
        error = FailedURL(
            url=url,
            error_type="parse_error",
            error_message=str(e),
            timestamp=datetime.now().isoformat()
        )
        logger.error(f"✗ Unexpected error processing {url}: {e}")
        return False, 0, error


# =============================================================================
# PHASE 4: USER STORY 2 - BATCH PROCESSING FUNCTIONS
# =============================================================================

async def check_url_exists(
    client: QdrantClient,
    collection_name: str,
    url: str
) -> bool:
    """
    Check if a URL already exists in Qdrant collection.

    Args:
        client: QdrantClient instance
        collection_name: Collection to search
        url: URL to check

    Returns:
        True if URL exists, False otherwise
    """
    try:
        results, _ = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="url",
                        match=models.MatchValue(value=url)
                    )
                ]
            ),
            limit=1
        )
        exists = len(results) > 0
        if exists:
            logger.info(f"URL already exists in collection: {url}")
        return exists

    except Exception as e:
        logger.warning(f"Failed to check if URL exists: {e}, assuming doesn't exist")
        return False


async def process_url_batch(
    urls: List[str],
    session: aiohttp.ClientSession,
    cohere_client: cohere.AsyncClient,
    qdrant_client: QdrantClient,
    config: IngestionConfig,
    skip_duplicates: bool,
    verbose: bool,
    semaphore: asyncio.Semaphore
) -> IngestionResult:
    """
    Process multiple URLs concurrently with rate limiting.

    Args:
        urls: List of URLs to process
        session: aiohttp ClientSession
        cohere_client: Cohere async client
        qdrant_client: Qdrant client
        config: Ingestion configuration
        skip_duplicates: Skip URLs already in Qdrant
        verbose: Show progress bar
        semaphore: Asyncio semaphore for concurrency control

    Returns:
        IngestionResult with aggregated results
    """
    result = IngestionResult()

    async def process_with_semaphore(url: str):
        """Process single URL with semaphore rate limiting."""
        async with semaphore:
            # Check for duplicates if requested
            if skip_duplicates:
                if await check_url_exists(qdrant_client, config.collection_name, url):
                    logger.info(f"⊘ Skipping duplicate URL: {url}")
                    return "skipped", 0, None

            # Process URL
            success, chunks_count, error = await process_single_url(
                url,
                session,
                cohere_client,
                qdrant_client,
                config
            )

            if success:
                return "success", chunks_count, None
            else:
                return "failed", 0, error

    # Process all URLs with progress bar
    if verbose:
        tasks = [process_with_semaphore(url) for url in urls]
        results_iter = tqdm(
            asyncio.as_completed(tasks),
            total=len(urls),
            desc="Processing URLs",
            unit="URL"
        )
        results = [await f for f in results_iter]
    else:
        tasks = [process_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Aggregate results
    for res in results:
        if isinstance(res, Exception):
            # Handle unexpected exceptions
            result.failed_count += 1
            error = FailedURL(
                url="unknown",
                error_type="parse_error",
                error_message=str(res),
                timestamp=datetime.now().isoformat()
            )
            result.failed_urls.append(error)
        else:
            status, chunks_count, error = res
            if status == "success":
                result.success_count += 1
                result.total_chunks += chunks_count
            elif status == "skipped":
                result.skipped_count += 1
            elif status == "failed":
                result.failed_count += 1
                if error:
                    result.failed_urls.append(error)

    return result


# =============================================================================
# PHASE 6: USER STORY 4 - RETRY LOGIC & ERROR CLASSIFICATION
# =============================================================================

def is_transient_error(exception: Exception) -> bool:
    """
    Classify errors as transient (retriable) or permanent.

    Args:
        exception: Exception to classify

    Returns:
        True if error is transient and should be retried
    """
    # HTTP transient errors
    if isinstance(exception, aiohttp.ClientError):
        if hasattr(exception, 'status'):
            # Retry on rate limits and server errors
            return exception.status in [429, 500, 502, 503, 504]
        # Retry on network errors
        return True

    # Qdrant transient errors
    if "QdrantConnection" in str(type(exception).__name__):
        return True

    # Cohere API transient errors
    if "CohereAPI" in str(type(exception).__name__):
        error_str = str(exception).lower()
        return "rate limit" in error_str or "429" in error_str or "500" in error_str

    return False


# =============================================================================
# MAIN ENTRY POINT (Placeholder)
# =============================================================================

async def main(
    urls: List[str],
    *,
    cohere_api_key: Optional[str] = None,
    qdrant_url: Optional[str] = None,
    qdrant_api_key: Optional[str] = None,
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
    """
    start_time = time.time()
    setup_logging(verbose)
    logger.info("=== Ingestion Pipeline Starting ===")

    # Load and validate configuration
    cohere_key, qdrant_url_val, qdrant_key, config = load_config(
        cohere_api_key=cohere_api_key,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key,
        collection_name=collection_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedding_model=embedding_model,
        embedding_dim=embedding_dim,
        batch_size=batch_size,
        max_retries=max_retries
    )

    logger.info(f"Configuration: {len(urls)} URLs, chunk_size={config.chunk_size}, overlap={config.chunk_overlap}")

    # Initialize clients
    cohere_client = cohere.AsyncClient(api_key=cohere_key)
    qdrant_client = QdrantClient(url=qdrant_url_val, api_key=qdrant_key)

    # Initialize Qdrant collection
    initialize_qdrant(qdrant_client, config.collection_name, config.embedding_dim)

    # Process URLs (Phase 4: batch processing with concurrency control)
    if not urls:
        logger.warning("No URLs provided")
        result = IngestionResult()
        result.execution_time_seconds = time.time() - start_time
        return result

    logger.info(f"Processing {len(urls)} URLs with concurrency limit={config.batch_size}")

    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(config.batch_size)

    async with aiohttp.ClientSession() as session:
        result = await process_url_batch(
            urls,
            session,
            cohere_client,
            qdrant_client,
            config,
            skip_duplicates,
            verbose,
            semaphore
        )

    # Calculate execution time
    result.execution_time_seconds = time.time() - start_time

    logger.info(f"=== Pipeline Complete: {result.success_count} success, {result.failed_count} failed, {result.total_chunks} chunks, {result.execution_time_seconds:.2f}s ===")

    return result


if __name__ == "__main__":
    # CLI entry point for testing
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <url1> [url2] [url3] ...")
        print("Example: python main.py https://docs.python.org/3/tutorial/index.html")
        sys.exit(1)

    test_urls = sys.argv[1:]
    result = asyncio.run(main(test_urls, verbose=True))

    print(f"\n[SUCCESS] {result.success_count} URLs processed")
    print(f"[FAILED] {result.failed_count} URLs failed")
    print(f"[SKIPPED] {result.skipped_count} URLs skipped")
    print(f"[CHUNKS] {result.total_chunks} total chunks created")
    print(f"[TIME] {result.execution_time_seconds:.2f}s")
    print(f"[SUCCESS RATE] {result.success_rate:.1f}%")
