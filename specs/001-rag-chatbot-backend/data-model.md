# Data Model: RAG Chatbot Backend

**Feature**: 001-rag-chatbot-backend
**Date**: 2025-12-24
**Phase**: Phase 1 (Design)

## Overview

This document defines the data entities, relationships, and validation rules for the RAG chatbot backend. The system manages three primary data domains: chat sessions, document chunks, and retrieval context.

---

## Entity Definitions

### 1. User

Represents a textbook reader who interacts with the chatbot.

**Attributes**:
- `user_id` (UUID, primary key): Unique identifier for the user
- `created_at` (timestamp): Account creation timestamp
- `last_active` (timestamp): Last interaction timestamp

**Validation Rules**:
- `user_id` must be a valid UUID v4
- `created_at` cannot be in the future
- `last_active` >= `created_at`

**State Transitions**:
- Created: User first interacts with chatbot
- Active: User has at least one session
- Inactive: No activity for 30+ days (for cleanup)

**Relationships**:
- One user has many sessions (1:N)

---

### 2. Session

Represents a conversation thread between a user and the chatbot.

**Attributes**:
- `session_id` (UUID, primary key): Unique session identifier
- `user_id` (UUID, foreign key): References user who owns this session
- `mode` (enum: "full_textbook" | "selection_only"): Query mode for this session
- `created_at` (timestamp): Session creation timestamp
- `last_active` (timestamp): Last message timestamp
- `metadata` (JSONB): Optional session context
  - `selected_text` (string, optional): User-selected text for selection mode
  - `chapter_context` (string, optional): Current textbook chapter
  - `title` (string, optional): User-provided session title

**Validation Rules**:
- `session_id` must be a valid UUID v4
- `mode` must be one of ["full_textbook", "selection_only"]
- `selected_text` required when `mode` = "selection_only"
- `last_active` >= `created_at`
- `metadata.selected_text` length must be <= 10,000 characters

**State Transitions**:
- Created: First message in new conversation
- Active: Has messages, `last_active` updated with each message
- Archived: Inactive for 7+ days (for cleanup)

**Relationships**:
- One session belongs to one user (N:1)
- One session has many messages (1:N)

---

### 3. Message

Represents a single message in a conversation (user query or assistant response).

**Attributes**:
- `message_id` (UUID, primary key): Unique message identifier
- `session_id` (UUID, foreign key): References session this message belongs to
- `role` (enum: "user" | "assistant"): Message sender
- `content` (text): Message text content
- `tokens` (integer, optional): Token count for this message
- `retrieved_chunks` (JSONB, optional): Retrieval metadata for assistant messages
  - `chunk_ids` (array of UUID): IDs of chunks retrieved from Qdrant
  - `similarity_scores` (array of float): Similarity scores for each chunk
  - `top_k` (integer): Number of chunks retrieved
- `created_at` (timestamp): Message creation timestamp

**Validation Rules**:
- `message_id` must be a valid UUID v4
- `role` must be one of ["user", "assistant"]
- `content` length must be >= 1 and <= 5,000 characters for user messages
- `content` length must be >= 1 and <= 2,000 characters for assistant messages
- `tokens` must be > 0 if provided
- `retrieved_chunks` only valid when `role` = "assistant"
- `retrieved_chunks.chunk_ids` length must equal `retrieved_chunks.similarity_scores` length

**State Transitions**:
- Created: Message stored immediately after generation/receipt
- Immutable: Messages are never modified after creation

**Relationships**:
- One message belongs to one session (N:1)

---

### 4. DocumentChunk

Represents a segment of textbook content indexed for retrieval.

**Attributes**:
- `chunk_id` (UUID, primary key): Unique chunk identifier
- `text` (text): The chunk text content
- `embedding` (vector[1536]): Text embedding vector (stored in Qdrant, not Postgres)
- `source_file` (string): Path to source markdown file
- `chapter` (string): Chapter name/number
- `section` (string): Section title
- `chunk_index` (integer): Position within the source document
- `token_count` (integer): Number of tokens in this chunk
- `created_at` (timestamp): Ingestion timestamp

**Validation Rules**:
- `chunk_id` must be a valid UUID v4
- `text` length must be >= 100 and <= 2,000 characters
- `embedding` dimension must be exactly 1536
- `source_file` must be a valid file path
- `token_count` must be > 0
- `chunk_index` must be >= 0

**State Transitions**:
- Ingested: Chunk created during textbook ingestion
- Updated: Re-ingestion updates existing chunk
- Deleted: Source content removed (rare)

**Relationships**:
- Independent entity (no foreign keys)
- Referenced by `Message.retrieved_chunks.chunk_ids`

**Storage Note**: Chunk metadata (all attributes except `embedding`) stored in Postgres for reference. Embeddings stored in Qdrant for vector search.

---

### 5. HealthStatus

Represents current system health state.

**Attributes**:
- `check_id` (UUID, primary key): Unique health check identifier
- `timestamp` (timestamp): Check execution time
- `service_status` (enum: "healthy" | "degraded" | "unhealthy"): Overall service status
- `qdrant_status` (enum: "connected" | "disconnected"): Qdrant connectivity
- `postgres_status` (enum: "connected" | "disconnected"): Neon Postgres connectivity
- `openai_status` (enum: "available" | "unavailable"): OpenAI API availability
- `response_time_ms` (integer): Health check response time in milliseconds
- `error_details` (JSONB, optional): Error information for failed checks

**Validation Rules**:
- `timestamp` cannot be in the future
- `response_time_ms` must be >= 0
- `error_details` only populated when status is not "healthy"

**State Transitions**:
- Checked: Health check executed every 60 seconds
- Logged: Result stored for monitoring
- Cleaned: Old records deleted after 7 days

**Relationships**:
- Independent entity (for monitoring only)

---

## Database Schema (Neon Postgres)

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('full_textbook', 'selection_only')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::JSONB,
    CONSTRAINT valid_selection_mode CHECK (
        mode != 'selection_only' OR (metadata->>'selected_text' IS NOT NULL)
    ),
    CONSTRAINT valid_last_active CHECK (last_active >= created_at)
);

-- Messages table
CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (char_length(content) >= 1),
    tokens INTEGER CHECK (tokens > 0),
    retrieved_chunks JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_message_length CHECK (
        role != 'user' OR char_length(content) <= 5000
    ),
    CONSTRAINT assistant_message_length CHECK (
        role != 'assistant' OR char_length(content) <= 2000
    )
);

-- Document chunks metadata (for reference only, embeddings in Qdrant)
CREATE TABLE document_chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL CHECK (char_length(text) BETWEEN 100 AND 2000),
    source_file VARCHAR(500) NOT NULL,
    chapter VARCHAR(200) NOT NULL,
    section VARCHAR(300) NOT NULL,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    token_count INTEGER NOT NULL CHECK (token_count > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health status table
CREATE TABLE health_status (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    service_status VARCHAR(20) NOT NULL CHECK (service_status IN ('healthy', 'degraded', 'unhealthy')),
    qdrant_status VARCHAR(20) NOT NULL CHECK (qdrant_status IN ('connected', 'disconnected')),
    postgres_status VARCHAR(20) NOT NULL CHECK (postgres_status IN ('connected', 'disconnected')),
    openai_status VARCHAR(20) NOT NULL CHECK (openai_status IN ('available', 'unavailable')),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    error_details JSONB
);

-- Indexes for performance
CREATE INDEX idx_sessions_user ON sessions(user_id, last_active DESC);
CREATE INDEX idx_messages_session ON messages(session_id, created_at ASC);
CREATE INDEX idx_messages_role ON messages(role, created_at DESC);
CREATE INDEX idx_chunks_source ON document_chunks(source_file, chunk_index);
CREATE INDEX idx_health_timestamp ON health_status(timestamp DESC);

-- Trigger to update session last_active on new message
CREATE OR REPLACE FUNCTION update_session_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE sessions
    SET last_active = NEW.created_at
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_last_active
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_session_last_active();
```

---

## Qdrant Collection Schema

```python
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

# Collection configuration
collection_name = "textbook_chunks"

vectors_config = VectorParams(
    size=1536,  # text-embedding-3-small dimensions
    distance=Distance.COSINE  # Optimal for OpenAI embeddings
)

# Payload schema (stored alongside vectors in Qdrant)
payload_schema = {
    "chunk_id": PayloadSchemaType.KEYWORD,  # UUID as string
    "text": PayloadSchemaType.TEXT,
    "source_file": PayloadSchemaType.KEYWORD,
    "chapter": PayloadSchemaType.KEYWORD,
    "section": PayloadSchemaType.KEYWORD,
    "chunk_index": PayloadSchemaType.INTEGER,
    "token_count": PayloadSchemaType.INTEGER
}

# HNSW index configuration for fast retrieval
hnsw_config = {
    "m": 16,  # Number of connections per layer
    "ef_construct": 100  # Quality of index construction
}
```

---

## Data Flow Diagrams

### Chat Flow (Full Textbook Mode)

```
1. User sends query
   ↓
2. Create/retrieve session
   ↓
3. Generate query embedding (OpenAI)
   ↓
4. Search Qdrant (top-k=5, threshold=0.7)
   ↓
5. Retrieve chat history (last 5 messages from Postgres)
   ↓
6. Build context (retrieved chunks + history)
   ↓
7. Generate response (OpenAI ChatCompletion)
   ↓
8. Store user message and assistant response in Postgres
   ↓
9. Return response to frontend
```

### Chat Flow (Selection-Only Mode)

```
1. User sends query + selected_text
   ↓
2. Create/retrieve session with metadata.selected_text
   ↓
3. NO vector search (hard grounding)
   ↓
4. Build context (only selected_text)
   ↓
5. Generate response with strict grounding prompt
   ↓
6. Store messages in Postgres
   ↓
7. Return response to frontend
```

### Ingestion Flow

```
1. Load markdown files from textbook
   ↓
2. Split by headers (MarkdownHeaderTextSplitter)
   ↓
3. Chunk with overlap (RecursiveCharacterTextSplitter, 512 tokens, 51 overlap)
   ↓
4. Generate embeddings (OpenAI text-embedding-3-small, batch)
   ↓
5. Store metadata in Postgres (document_chunks table)
   ↓
6. Store vectors + payload in Qdrant
   ↓
7. Return ingestion summary
```

---

## Data Retention & Cleanup

### Session Archival
- Sessions inactive for 7+ days marked as archived
- Messages retained for reference but excluded from active queries

### Health Check Cleanup
- Health check records older than 7 days deleted automatically
- Keeps last 10,080 records (7 days * 24 hours * 60 minutes)

### Chunk Updates
- Re-ingestion overwrites existing chunks with same source_file + chunk_index
- Orphaned chunks (source file deleted) remain until manual cleanup

### SQL Cleanup Queries

```sql
-- Archive old sessions (run daily)
UPDATE sessions
SET metadata = jsonb_set(metadata, '{archived}', 'true')
WHERE last_active < CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND metadata->>'archived' IS NULL;

-- Delete old health checks (run daily)
DELETE FROM health_status
WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '7 days';

-- Find orphaned chunks (for manual review)
SELECT chunk_id, source_file, chapter
FROM document_chunks
WHERE source_file NOT IN (SELECT DISTINCT source_file FROM document_chunks WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '30 days');
```

---

## Validation & Constraints Summary

| Entity | Key Constraints |
|--------|----------------|
| User | `user_id` unique, `last_active` >= `created_at` |
| Session | `mode` enum, `selected_text` required for selection mode, `last_active` >= `created_at` |
| Message | `role` enum, content length limits, `retrieved_chunks` only for assistant |
| DocumentChunk | text length 100-2000 chars, token_count > 0, chunk_index >= 0 |
| HealthStatus | timestamp not future, response_time >= 0, error_details conditional |

---

## Performance Considerations

### Postgres Indexes
- `idx_sessions_user`: Fast session lookup by user
- `idx_messages_session`: Fast message retrieval for conversation history
- `idx_chunks_source`: Fast chunk lookup by source file

### Qdrant Optimizations
- HNSW index for approximate nearest neighbor search
- Cosine distance for semantic similarity
- Payload index on `source_file` and `chapter` for metadata filtering

### Query Patterns
- Limit conversation history to last 5 messages (prevents context window overflow)
- Use pagination for session list (100 sessions per page)
- Batch embedding generation (up to 2048 chunks per API call)

---

## Security Notes

- UUIDs prevent enumeration attacks
- Cascade deletes ensure referential integrity
- JSONB fields sanitized to prevent injection
- Content length limits prevent DoS attacks
- No PII stored in messages (anonymous usage)
