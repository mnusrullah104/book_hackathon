---
id: 002
title: Create implementation plan
stage: plan
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-web-embedding-ingestion
branch: 002-web-embedding-ingestion
user: Muhammad Nasrullah
command: /sp.plan
labels: ["planning", "architecture", "rag", "cohere", "qdrant", "web-ingestion", "single-file"]
links:
  spec: specs/002-web-embedding-ingestion/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-web-embedding-ingestion/plan.md
 - specs/002-web-embedding-ingestion/research.md
 - specs/002-web-embedding-ingestion/data-model.md
 - specs/002-web-embedding-ingestion/quickstart.md
 - specs/002-web-embedding-ingestion/contracts/python-interface.md
 - CLAUDE.md (agent context updated)
 - history/prompts/002-web-embedding-ingestion/002-create-implementation-plan.plan.prompt.md
tests:
 - Constitution compliance check (6/6 principles passed)
 - Design validation (all requirements mapped to components)
---

## Prompt

Plan the website ingestion and embedding pipeline for the RAG system

Create backend/ folder and initialize project using UV package manager

Inside backend/, create a single main.py containing all ingestion logic

In main.py: fetch URLs → extract & chunk text → generate embeddings (Cohere) → store in Qdrant

Define Qdrant collection schema and metadata structure

Implement a final main() function that orchestrates the full pipeline execution

## Response snapshot

Successfully created complete implementation plan for Website URL Embedding Ingestion Pipeline with single-file architecture.

**Planning Workflow Completed**:
1. ✅ Setup: Ran setup-plan.ps1, loaded spec and constitution
2. ✅ Phase 0 (Research): Generated research.md with 7 technical decisions
3. ✅ Phase 1 (Design): Generated data-model.md, contracts/, and quickstart.md
4. ✅ Agent Context: Updated CLAUDE.md with Python 3.9+, Cohere, Qdrant, LangChain stack

**Research Decisions (research.md)**: 7 key areas resolved
1. **HTML Parsing**: BeautifulSoup4 with html.parser (robust, simple, handles malformed HTML)
2. **Chunking**: LangChain RecursiveCharacterTextSplitter (512 tokens, 50 overlap, semantic boundaries)
3. **Embeddings**: Cohere embed-english-v3.0 with search_document input type (1024-dim, batch API)
4. **Qdrant Schema**: Single collection "web_documents", COSINE distance, indexed URL field for dedup
5. **Batch Processing**: asyncio with Semaphore(5) concurrency, aiohttp for async HTTP
6. **Retry Strategy**: Exponential backoff with jitter, max 3 retries for transient errors only
7. **Configuration**: Environment variables + function parameters (no config file for MVP)

**Data Model (data-model.md)**: 5 entities defined
- IngestionConfig (configuration parameters with validation)
- WebDocument (fetched HTML before processing)
- TextChunk (segmented text with metadata)
- Embedding (vector representation from Cohere)
- QdrantPoint (complete storage entity in vector DB)

**Qdrant Collection Schema**:
```python
{
  "vectors": {"size": 1024, "distance": "Cosine"},
  "payload_indexes": ["url" (keyword), "timestamp" (datetime)]
}
```

**Python Interface (contracts/python-interface.md)**: Complete programmatic API
- **Main function**: `async def main(urls, *, cohere_api_key, qdrant_url, ...) -> IngestionResult`
- **Result types**: IngestionResult (success/failed/skipped counts, execution time)
- **Exception types**: ConfigurationError, QdrantConnectionError, CohereAPIError
- **4 usage examples**: Single URL, batch ingestion, FastAPI integration, error handling
- **Validation rules**: All parameters validated with clear error messages

**Quickstart Guide (quickstart.md)**: 7-step setup (15-30 min completion time)
1. Get API credentials (Cohere + Qdrant Cloud)
2. Project setup with UV package manager
3. Configure environment (.env file)
4. Create main.py (implementation in /sp.implement phase)
5. Run first ingestion (single URL test)
6. Verify in Qdrant (query test)
7. Batch ingestion (10 URLs)

**Implementation Plan (plan.md)**: Complete architecture document
- **Single-file architecture**: All logic in backend/main.py (~500-800 lines) per user request
- **UV package manager**: Initialize with `uv init`, install deps with `uv pip install`
- **Async architecture**: asyncio for I/O-bound pipeline, 10x throughput vs. sync
- **3 implementation phases**:
  - Phase 1: Core pipeline (US1 - single URL end-to-end)
  - Phase 2: Batch processing (US2 - concurrent multi-URL)
  - Phase 3: Config & resilience (US3/4 - retry logic, validation)
- **Constitution compliance**: ✅ All 6 principles passed (spec-first, accuracy, clarity, AI-native, transparency, modular)
- **Risk analysis**: 6 risks identified with mitigations
- **Testing strategy**: Unit tests (pytest-asyncio) + integration tests with real APIs
- **Dependencies**: 10 packages (BeautifulSoup4, aiohttp, cohere, qdrant-client, langchain, tiktoken, tenacity, pydantic, python-dotenv, tqdm)

**Design Decisions**:
1. **Single-file implementation**: User requirement, simplifies deployment, ~500-800 lines
2. **UV package manager**: 10-100x faster than pip, user-specified
3. **Async architecture**: asyncio for I/O-bound workload, Semaphore(5) concurrency control
4. **Config strategy**: Env vars for secrets, function params for operational settings
5. **Error handling**: Fail-fast on config errors, graceful degradation on runtime errors

**Performance Targets** (from spec success criteria):
- Single URL latency: < 5s (fetch → store)
- Batch success rate: ≥ 95% (excluding 404s, timeouts)
- Embedding generation: < 2s/chunk (Cohere API latency)
- Qdrant queryability: Immediate (zero-delay after upsert)
- Developer integration: < 30min (quickstart completion)

**Project Structure** (per user requirements):
```
backend/
├── main.py              # Single file with all logic
├── .env                 # API keys (COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY)
├── .env.example         # Template
├── requirements.txt     # Generated by UV
└── README.md            # Integration guide
```

## Outcome

- ✅ Impact: Complete implementation plan with single-file architecture, ready for task generation (/sp.tasks)
- 🧪 Tests: Constitution check passed (6/6 principles), design validated against 15 functional requirements
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, contracts/python-interface.md, PHR), CLAUDE.md updated
- 🔁 Next prompts: Run `/sp.tasks` to generate atomic implementation tasks, then `/sp.implement` to build backend/main.py
- 🧠 Reflection: Single-file architecture unusual but matches user's explicit requirement for simplicity. All design decisions traced back to spec requirements or user instructions. UV package manager integrated seamlessly. Cohere free tier rate limits (10 req/min) addressed with Semaphore(5) concurrency and exponential backoff.

## Evaluation notes (flywheel)

- Failure modes observed: None - all Phase 0 and Phase 1 planning steps completed successfully
- Graders run and results (PASS/FAIL): PASS - Constitution check 6/6, all spec requirements mapped to design components, Qdrant schema validated
- Prompt variant (if applicable): User provided explicit architecture requirements (single main.py, UV package manager, Cohere+Qdrant stack)
- Next experiment (smallest change to try): Generate tasks with /sp.tasks (break plan into atomic implementation steps), then implement backend/main.py with /sp.implement
