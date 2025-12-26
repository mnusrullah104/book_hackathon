# Implementation Plan: RAG Retrieval Validation and Testing

**Branch**: `003-rag-retrieval-validation` | **Date**: 2025-12-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-rag-retrieval-validation/spec.md`

## Summary

Build retrieval and validation functions for the RAG ingestion pipeline that query Qdrant vector database, retrieve relevant chunks with metadata, and validate end-to-end correctness. Per user requirements, implementation will be in a single `backend/retrieve.py` file with test scripts demonstrating query examples and automated validation assertions.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: Cohere SDK (query embeddings), Qdrant Client (vector search), python-dotenv (config)
**Storage**: Qdrant Cloud (vector database, existing "web_documents" collection with 109+ chunks)
**Testing**: Assertion-based validation scripts (pytest-style but minimal, not full test suite)
**Target Platform**: Linux/macOS/Windows (cross-platform Python)
**Project Type**: Single-file backend module (backend/retrieve.py)
**Performance Goals**: <1 second query response, >0.7 similarity for relevant content, 100% metadata completeness
**Constraints**: Single-file implementation, no chatbot logic, minimal dependencies, async-compatible
**Scale/Scope**: Query against 100+ chunks, validate 4 modules, 5-10 sample test queries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Compliance Review

| Principle | Status | Notes |
|-----------|--------|-------|
| **Spec-first development** | ✅ PASS | Formal spec created with requirements, user stories, acceptance criteria |
| **Technical accuracy** | ✅ PASS | Uses existing Cohere/Qdrant setup, reproducible with env vars |
| **Clarity for developers** | ✅ PASS | Validation scripts with examples, clear test assertions |
| **AI-native architecture** | ✅ PASS | RAG retrieval with vector search and semantic embeddings |
| **End-to-end transparency** | ✅ PASS | Logging, validation reports, metadata verification |
| **Modular content** | ✅ PASS | Single-file retrieve.py, no filler, production-quality validation |

**Verdict**: ✅ All gates passed. No constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-rag-retrieval-validation/
├── spec.md              # Feature specification (4 user stories, 15 requirements)
├── plan.md              # This file - implementation plan
├── research.md          # Technical decisions (Phase 0)
├── data-model.md        # Entity definitions (Phase 1)
├── quickstart.md        # Testing guide (Phase 1)
├── contracts/
│   └── python-interface.md  # Public API contract
└── checklists/
    └── requirements.md  # Spec quality validation (12/12 passed)
```

### Source Code (repository root)

Per user requirements: **Single-file implementation in backend/retrieve.py**

```text
backend/
├── main.py              # Existing ingestion pipeline (from 002-web-embedding-ingestion)
├── retrieve.py          # NEW: Retrieval and validation functions (this feature)
├── test_retrieval.py    # NEW: Sample queries and validation tests
├── .env                 # Environment variables (shared with main.py)
├── .env.example         # Template (already exists)
├── requirements.txt     # Dependencies (already includes Cohere + Qdrant)
└── README.md            # Integration instructions (update with retrieval examples)
```

**Structure Decision**: User requested single-file implementation (`backend/retrieve.py`) to keep retrieval logic separate from ingestion (`backend/main.py`). This allows:
- Independent testing of retrieval without running ingestion
- Modular reuse in future FastAPI integration
- Clear separation of concerns (ingest vs. query)
- Shared dependencies and configuration with existing pipeline

## Complexity Tracking

> **No constitution violations - section left empty per instructions.**

## Design Decisions

### 1. Separate Retrieval File (retrieve.py)

**Decision**: Create `backend/retrieve.py` separate from ingestion logic in `main.py`

**Rationale** (from user requirements):
- User explicitly requested: "Create a single file retrieve.py inside backend/"
- Separation of concerns: ingestion vs. retrieval are distinct operations
- Independent testing: can test retrieval without re-running ingestion
- Modular for future integration: easier to import into FastAPI or agent code
- Shared dependencies: reuses Cohere + Qdrant clients from existing setup

**Trade-offs**:
- ✅ **Pro**: Clean separation, easier to understand and test
- ✅ **Pro**: Modular for agent/API integration later
- ❌ **Con**: Some code duplication (config loading, client initialization)

**Mitigation**: Share configuration via environment variables, import common utilities if needed

---

### 2. Query Embedding Strategy

**Decision**: Use same Cohere model (embed-english-v3.0) with `search_query` input type for queries

**Rationale**:
- **Model consistency**: Must match ingestion model for accurate similarity
- **Input type difference**: Use `search_query` for queries vs. `search_document` for ingestion (Cohere best practice)
- **Dimension match**: 1024-dim vectors for both query and stored documents
- **Batch API**: Not needed for queries (typically 1 query at a time)

**Pattern**:
```python
async def embed_query(query_text: str, cohere_client) -> List[float]:
    response = await cohere_client.embed(
        texts=[query_text],
        model="embed-english-v3.0",
        input_type="search_query"  # Different from ingestion's "search_document"
    )
    return response.embeddings[0]
```

---

### 3. Qdrant Search Strategy

**Decision**: Use Qdrant's `search()` API with COSINE distance and configurable top_k

**Rationale**:
- **search() vs. query()**: `search()` is simpler for basic vector similarity (no filters in MVP)
- **COSINE distance**: Matches collection configuration from ingestion
- **Top_k parameter**: Configurable result count (default 5, per spec)
- **Metadata retrieval**: `with_payload=True` to get full metadata
- **Score threshold**: Optional minimum similarity filter (default 0.0 to allow all results)

**Pattern**:
```python
results = client.search(
    collection_name="web_documents",
    query_vector=query_embedding,
    limit=top_k,
    with_payload=True,
    score_threshold=0.7  # Optional relevance filter
)
```

---

### 4. Validation Strategy

**Decision**: Assertion-based validation in test scripts (not pytest framework)

**Rationale** (from user constraints):
- User specified: "minimal test queries for validation" (not comprehensive test suite)
- Simple assertions in test scripts vs. full pytest framework
- Focus on smoke tests: dimensions, metadata presence, similarity scores
- Manual execution by developers for verification

**Validation Types**:
1. **Dimension check**: Verify all vectors are 1024-dim
2. **Metadata check**: Ensure required fields (url, chunk_text, timestamp) present
3. **Similarity check**: Embed same text twice, verify >0.99 similarity
4. **Retrieval check**: Query for known content, verify correct chunks returned

---

### 5. Error Handling for Retrieval

**Decision**: Return empty results for no matches, fail-fast for configuration errors

**Rationale**:
- **Empty results**: Natural outcome, not an error (query may have no relevant docs)
- **Configuration errors**: Missing API keys → fail immediately
- **Qdrant unavailable**: Fail with clear error message
- **Invalid parameters**: Validate before making API calls

**Categories**:
- **Valid query, no results**: Return empty list, log info
- **Invalid query** (empty string): Raise ValueError with guidance
- **Connection failure**: Raise QdrantConnectionError
- **API failure**: Raise CohereAPIError

---

## Implementation Roadmap

Per `/sp.plan` command scope, this plan defines WHAT to build, not HOW. The `/sp.tasks` command will break this into atomic implementation tasks.

### Phase 1: Core Retrieval (User Story 1 - P1)

**Goal**: Basic vector search with similarity scoring

**Components**:
1. **Query Embedding**: Cohere API call with `search_query` input type
2. **Vector Search**: Qdrant search() with COSINE distance
3. **Result Formatting**: RetrievedChunk objects with score + metadata
4. **Main Function**: `search(query_text, top_k=5)` async interface

**Success Criteria**: Query "ROS 2 fundamentals", verify Module 1 chunks returned with >0.7 similarity

---

### Phase 2: Metadata Filtering (User Story 2 - P2)

**Goal**: Filter results by URL patterns and verify metadata

**Components**:
1. **Filter Support**: Qdrant Filter API for URL pattern matching
2. **Metadata Validation**: Check all required fields present
3. **URL Pattern Filter**: Filter by module (e.g., "module-1", "module-2")

**Success Criteria**: Filter for Module 2 content, verify only Module 2 chunks returned

---

### Phase 3: End-to-End Testing (User Story 3 - P2)

**Goal**: Validate full ingestion-to-retrieval flow

**Components**:
1. **Test Document Ingestion**: Ingest small test URL
2. **Retrieval Verification**: Query for test content, verify present
3. **Consistency Check**: Re-embed same text, verify high similarity

**Success Criteria**: Ingest test URL, query for its content, verify retrieval with >0.95 similarity

---

### Phase 4: Automated Validation (User Story 4 - P3)

**Goal**: Assertion-based validation suite

**Components**:
1. **Dimension Validation**: Check all vectors are 1024-dim
2. **Metadata Completeness**: Verify no missing fields
3. **Duplicate Detection**: Check for unintentional duplicate URLs
4. **Validation Report**: Generate pass/fail report

**Success Criteria**: Run validation suite, verify 100% pass rate on dimension/metadata checks

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Query embedding differs from ingestion | Low | Critical | Use same model, validate dimensions match |
| Empty result sets confuse developers | Medium | Low | Clear logging, return empty list vs. error |
| Metadata fields missing/corrupted | Low | Medium | Validation checks, fail-fast on missing data |
| Similarity scores misinterpreted | Medium | Low | Document score ranges, provide examples |
| Qdrant unavailable during testing | Low | Medium | Graceful error messages, retry suggestions |

---

## Testing Strategy

### Sample Test Queries

```python
# Test 1: Module-specific query
query = "How do I set up ROS 2 for humanoid robots?"
# Expected: Module 1 chunks with >0.7 similarity

# Test 2: Cross-module query
query = "NVIDIA Isaac Sim for robot simulation"
# Expected: Module 3 chunks ranked highest

# Test 3: VLA integration query
query = "voice to action pipeline for autonomous robots"
# Expected: Module 4 chunks in top results

# Test 4: Empty results query
query = "quantum computing algorithms"
# Expected: Empty list or very low similarity scores
```

### Validation Assertions

```python
# Assert 1: Dimension consistency
assert all(len(v) == 1024 for v in vectors), "All vectors must be 1024-dim"

# Assert 2: Metadata completeness
required_fields = ["url", "chunk_text", "timestamp", "chunk_index"]
assert all(f in chunk.metadata for f in required_fields), "Missing metadata"

# Assert 3: Similarity consistency
embedding1 = await embed_query("test text")
embedding2 = await embed_query("test text")
similarity = cosine_similarity(embedding1, embedding2)
assert similarity > 0.99, f"Identical text similarity too low: {similarity}"
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Query response time | < 1s | Time from query to results |
| Similarity for relevant content | > 0.7 | Score for module-matching queries |
| Metadata completeness | 100% | All chunks have required fields |
| End-to-end test success | 100% | Ingest → retrieve test passes |
| Embedding consistency | > 0.99 | Same text embedded twice |
| Validation test pass rate | 100% | Automated assertions pass |
| Developer setup time | < 10min | Run test queries from README |

---

## Next Steps

1. **Run `/sp.tasks`**: Break this plan into atomic implementation tasks
2. **Create Phase 0 (research.md)**: Document Qdrant search API patterns and best practices
3. **Create Phase 1 (data-model.md, contracts/)**: Define RetrievalResult and API contracts
4. **Run `/sp.implement`**: Execute tasks to build `backend/retrieve.py`

---

**Plan Complete**: Ready for Phase 0 research and data modeling.
