# Research: RAG Chatbot Backend Technical Decisions

**Feature**: 001-rag-chatbot-backend
**Date**: 2025-12-24
**Phase**: Phase 0 (Research)

## Overview

This document captures research findings and technical decisions for building a FastAPI-based RAG chatbot backend that serves an AI-native textbook on Physical AI & Humanoid Robotics. All decisions prioritize reliability, grounding accuracy, and hackathon MVP viability.

---

## 1. Chunking Strategy

**Decision**: Markdown-aware semantic chunking with RecursiveCharacterTextSplitter (512 tokens, 51 token overlap)

**Rationale**:
- Markdown-aware chunking outperforms fixed-size by 5-10 percentage points when document structure is available
- RecursiveCharacterTextSplitter delivers 85-90% recall without computational overhead of pure semantic chunking
- Educational textbook content has clear structural boundaries (headings, sections) that should be preserved
- 512-token chunks provide optimal balance between context completeness and retrieval precision
- 10% overlap (51 tokens) prevents information loss at chunk boundaries

**Alternatives Considered**:
- **Fixed-size chunking (256 tokens)**: Rejected - breaks sentences and ignores context boundaries
- **Pure semantic chunking**: Rejected - 70% accuracy improvement but computationally expensive and slowest
- **Larger chunks (1024+ tokens)**: Rejected - reduces retrieval precision and increases noise

**Implementation Notes**:
```python
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Stage 1: Split by markdown headers to preserve structure
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")]
)

# Stage 2: Further split with recursive splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=51,
    separators=["\\n\\n", "\\n", " ", ""]
)

# Preserve code blocks and mathematical notation as atomic units
# Add metadata: section title, chapter, page number for citation
```

---

## 2. Retrieval Configuration

**Decision**: Top-k=5 with adaptive similarity threshold (0.7 baseline, 0.75+ for selection-only mode)

**Rationale**:
- Educational content requires balance between context richness (higher k) and response accuracy (lower k)
- Top-k=5 provides sufficient context without overwhelming LLM attention mechanism
- Similarity threshold of 0.7 filters low-relevance chunks while maintaining recall
- Selection-only queries require stricter threshold (0.75+) to prevent hallucination
- Adaptive thresholds allow mode-specific optimization

**Alternatives Considered**:
- **Top-k=3**: Rejected - insufficient context for complex educational questions spanning multiple concepts
- **Top-k=10**: Rejected - increases noise and reduces answer precision, higher latency
- **Fixed threshold across all queries**: Rejected - different query types need different strictness levels

**Implementation Notes**:
```python
# Standard retrieval (full textbook search)
standard_retrieval_config = {
    "top_k": 5,
    "similarity_threshold": 0.7,
    "rerank": True,
    "diversity_penalty": 0.3
}

# Selection-based retrieval (user-selected text)
selection_retrieval_config = {
    "top_k": 3,
    "similarity_threshold": 0.75,
    "rerank": False,
    "diversity_penalty": 0.0
}

# Minimum retrieval guarantee: return at least 2 chunks regardless of threshold
```

---

## 3. Selection-Based Grounding

**Decision**: Hard grounding with explicit citation requirement for selection-only answers

**Rationale**:
- 96% hallucination reduction achieved by combining strict grounding with guardrails (Stanford 2024)
- Educational context demands factual accuracy over answer completeness
- Selection-only mode explicitly signals user wants answer from THAT text only
- De-hallucination methods reduced hallucination rate from 65.79% to 13.88% in testing
- Clear user expectation: "explain THIS text" not "explain THIS topic"

**Alternatives Considered**:
- **Soft grounding with limited vector search**: Rejected - introduces hallucination risk, violates user expectation
- **No grounding enforcement**: Rejected - unacceptable for educational content
- **Conditional retrieval with validation**: Considered but adds complexity for hackathon MVP

**Implementation Notes**:
```python
SELECTION_ONLY_PROMPT = """
You are answering questions STRICTLY based on the user-selected text provided below.

CRITICAL RULES:
1. ONLY use information from the selected text
2. If the answer is not in the selected text, respond: "I cannot answer this question based on the selected text alone."
3. DO NOT use your general knowledge or training data
4. Cite specific sentences from the selection in your answer
5. If the selection is ambiguous, ask for clarification

Selected Text:
{selected_text}

Question: {question}
"""

# Post-generation validation (optional)
def validate_selection_answer(answer: str, selected_text: str) -> bool:
    # Use entailment model to check if answer is grounded in selection
    pass
```

---

## 4. Chat History Architecture

**Decision**: Stored sessions in Neon Postgres with UUID session IDs, stateless API layer

**Rationale**:
- Enables conversation continuity across page refreshes and devices (essential for educational use)
- Stateless API design allows any server instance to handle any request (scalability)
- PostgreSQL provides ACID guarantees for chat history integrity
- Neon's free tier (512MB storage, 3GB data transfer) sufficient for hackathon demo
- Session-based architecture simplifies debugging and user support
- Students expect to return to previous conversations when learning complex topics

**Alternatives Considered**:
- **Fully stateless (client sends full history)**: Rejected - high bandwidth usage, security risk, poor UX for long conversations
- **Server-side stateful sessions**: Rejected - complicates deployment, doesn't scale horizontally
- **Redis-only storage**: Rejected - adds another dependency, less reliable for persistent history

**Implementation Notes**:
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    mode VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(session_id),
    role VARCHAR(20),
    content TEXT NOT NULL,
    tokens INTEGER,
    retrieved_chunks JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_messages ON messages(session_id, created_at);
CREATE INDEX idx_session_last_active ON sessions(last_active);
```

**Session ID Strategy**: Server-generated UUIDs on first message; client stores and includes in subsequent requests.

---

## 5. Deployment Platform

**Decision**: Render for FastAPI backend deployment

**Rationale**:
- Native ASGI/Uvicorn support (critical for FastAPI's async event loop)
- Flat-rate pricing ($7/month starter) with predictable costs for demos
- Auto-deploy from Git with zero DevOps configuration
- Managed PostgreSQL integration compatible with external Neon connection
- HTTPS endpoints by default with automatic SSL certificates
- Excellent documentation for FastAPI deployment
- Health check support for uptime monitoring

**Alternatives Considered**:
- **Railway**: Rejected - usage-based pricing unpredictable for demos, $0.10/GB egress costly, free tier only $5 credits
- **Fly.io**: Rejected - requires more infrastructure experience, VM-based deployment adds complexity, better for globally distributed apps
- **Vercel/AWS Lambda**: Rejected - cold start issues for RAG pipelines, function timeout limits problematic

**Implementation Notes**:
```yaml
# render.yaml
services:
  - type: web
    name: rag-chatbot-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
    healthCheckPath: /health
    autoDeploy: true
```

**CORS Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 6. OpenAI Integration

**Decision**: OpenAI SDK (openai-python) with direct ChatCompletion API

**Rationale**:
- OpenAI Agents SDK lacks RAG-specific primitives (no vector search integration)
- Direct ChatCompletion API provides fine-grained control over grounding and context
- Simpler architecture for hackathon MVP - avoid unnecessary abstraction layers
- Better documentation and examples for RAG use cases with direct API
- Agents SDK overhead not justified without multi-agent workflows
- Clear separation between retrieval (Qdrant) and generation (OpenAI)

**Alternatives Considered**:
- **OpenAI Agents SDK**: Rejected - designed for multi-agent orchestration, not RAG optimization; adds complexity without benefits
- **LangChain**: Rejected - heavy dependency, over-engineered for this use case, rapid breaking changes
- **LlamaIndex**: Rejected - adds abstraction layer; direct implementation preferred for hackathon clarity

**Implementation Notes**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_answer(
    query: str,
    retrieved_chunks: list[str],
    mode: str,
    chat_history: list[dict]
) -> str:
    context = "\\n\\n".join([
        f"[Chunk {i+1}]\\n{chunk}"
        for i, chunk in enumerate(retrieved_chunks)
    ])

    system_prompt = (
        SELECTION_ONLY_PROMPT if mode == "selection_only"
        else FULL_TEXTBOOK_PROMPT
    )

    messages = [
        {"role": "system", "content": system_prompt},
        *chat_history[-5:],
        {"role": "user", "content": f"Context:\\n{context}\\n\\nQuestion: {query}"}
    ]

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=800
    )

    return response.choices[0].message.content
```

**Model Choice**: gpt-4o-mini for cost-effective demo with sufficient quality.

---

## 7. Embedding Strategy

**Decision**: text-embedding-3-small with 1536 dimensions

**Rationale**:
- 6.5x cheaper than text-embedding-3-large ($0.02 vs $0.13 per million tokens)
- 75.8% accuracy sufficient for educational content retrieval
- Faster embedding generation crucial for real-time hackathon demos
- 1536 dimensions provide adequate semantic understanding for textbook content
- Cost savings redirect to LLM API calls (more valuable for demo UX)
- OpenAI embeddings integrate seamlessly with Qdrant

**Alternatives Considered**:
- **text-embedding-3-large**: Rejected - 80.5% accuracy only 5% better, 6.5x cost not justified for MVP
- **Open-source embeddings (sentence-transformers)**: Rejected - requires hosting, adds infrastructure complexity
- **Shortened embeddings (768 dimensions)**: Considered but minimal benefit at hackathon scale

**Implementation Notes**:
```python
from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams

client = AsyncOpenAI()
qdrant = AsyncQdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

await qdrant.create_collection(
    collection_name="textbook_chunks",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

async def embed_text(text: str) -> list[float]:
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        encoding_format="float"
    )
    return response.data[0].embedding

# Batch embedding for efficiency (max 2048 per request)
async def embed_chunks(chunks: list[str]) -> list[list[float]]:
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks,
        encoding_format="float"
    )
    return [item.embedding for item in response.data]
```

---

## Additional Implementation Recommendations

### Error Handling & Monitoring

```python
from fastapi import HTTPException
import logging

async def safe_rag_query(query: str) -> str:
    try:
        return await rag_pipeline(query)
    except Exception as e:
        logging.error(f"RAG pipeline error: {e}")
        return "I'm experiencing technical difficulties. Please try again."

# Rate limiting for free tier protection
from slowapi import Limiter
limiter = Limiter(key_func=lambda: request.client.host)

@app.post("/api/chat")
@limiter.limit("30/minute")
async def chat(request: ChatRequest):
    pass
```

### Environment Configuration

```bash
# .env.example
OPENAI_API_KEY=sk-...
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=...
DATABASE_URL=postgresql://user:pass@db.neon.tech/chathistory
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

---

## Architecture Summary

```
Frontend (Vercel)
    |
    | HTTPS + CORS
    v
FastAPI Backend (Render)
    |
    +-- Chat History --> Neon Postgres
    |
    +-- Vector Search --> Qdrant Cloud
    |
    +-- Embeddings & LLM --> OpenAI API

Flow:
1. User query -> FastAPI endpoint
2. Retrieve chat history from Postgres
3. Generate query embedding (text-embedding-3-small)
4. Search Qdrant for top-5 chunks (similarity > 0.7)
5. Build context with retrieved chunks + history
6. Generate answer with GPT-4o-mini (hard grounding for selection mode)
7. Store conversation in Postgres
8. Return response to frontend
```

---

## Cost Estimation (Hackathon Demo)

**Assumptions**: 100 demo conversations, 10 messages per conversation, 5 chunks per query

- **OpenAI Embeddings**: ~50K tokens = $1.00
- **OpenAI LLM**: ~500K tokens = $1.50 (gpt-4o-mini)
- **Qdrant Cloud**: Free tier (1GB storage, 100K vectors)
- **Neon Postgres**: Free tier (512MB, 3GB transfer)
- **Render**: $7/month (or free tier with sleep mode)

**Total**: ~$9.50 for hackathon demo with professional infrastructure

---

## References

- Document Chunking for RAG: 9 Strategies Tested (70% Accuracy Boost 2025)
- Best Chunking Strategies for RAG in 2025
- Retrieval-augmented generation for educational application: A systematic survey
- The 2025 Guide to Retrieval-Augmented Generation (RAG)
- Grounding AI reduces hallucinations and increases response accuracy
- Building Stateful Conversations with Postgres and LLMs
- Python Hosting Options Compared: Vercel, Fly.io, Render, Railway (2025)
- OpenAI Agents SDK Documentation
- Comparing OpenAI's Text-Embedding-3-Small and Text-Embedding-3-Large
- Hallucination Mitigation for Retrieval-Augmented Large Language Models
