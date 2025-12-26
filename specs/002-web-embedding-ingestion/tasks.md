---
description: "Implementation tasks for Website URL Embedding Ingestion Pipeline"
---

# Tasks: Website URL Embedding Ingestion Pipeline

**Feature**: 002-web-embedding-ingestion
**Input**: Design documents from `/specs/002-web-embedding-ingestion/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT included per spec (only backend pipeline implementation)

**Organization**: Tasks organized by user story to enable independent implementation and testing

## Format: `- [ ] [ID] [P?] [Story] Description`

- **Checkbox**: `- [ ]` (markdown checkbox)
- **[ID]**: Sequential task number (T001, T002, etc.)
- **[P]**: Task can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4) - only for user story phases
- **Description**: Clear action with exact file path

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure and dependencies using UV package manager

- [x] T001 Initialize Python project using UV package manager in backend/ directory
- [x] T002 [P] Create backend/.env.example with template for COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY
- [x] T003 [P] Create backend/README.md with integration instructions and quickstart reference
- [x] T004 Install core dependencies via UV: beautifulsoup4, aiohttp, cohere, qdrant-client, langchain, tiktoken
- [x] T005 [P] Install utility dependencies via UV: tenacity, pydantic, python-dotenv, tqdm
- [x] T006 Generate backend/requirements.txt from UV lockfile for pip compatibility
- [x] T007 [P] Update .gitignore to exclude backend/.env, __pycache__, *.pyc

---

## Phase 2: Foundational (Core Infrastructure)

**Purpose**: Shared utilities and validation that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Create IngestionConfig data class with validation rules in backend/main.py
- [x] T009 Create IngestionResult and FailedURL data classes in backend/main.py
- [x] T010 [P] Define custom exception types: IngestionError, ConfigurationError, QdrantConnectionError, CohereAPIError in backend/main.py
- [x] T011 [P] Implement config loading function with env var fallbacks in backend/main.py
- [x] T012 Implement input validation function for chunk_size, chunk_overlap, embedding_dim, batch_size parameters in backend/main.py
- [x] T013 [P] Setup structured logging configuration with INFO and ERROR levels in backend/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Single URL Content Ingestion (Priority: P1) 🎯 MVP

**Goal**: Ingest content from a single URL, generate embeddings, and store in Qdrant

**Independent Test**: Provide https://docs.python.org/3/tutorial/index.html, verify content extracted, embeddings generated, data stored in Qdrant, and retrievable via search

### Implementation for User Story 1

- [x] T014 [P] [US1] Implement async fetch_url function using aiohttp with timeout handling in backend/main.py
- [x] T015 [P] [US1] Implement extract_text function using BeautifulSoup to remove script/style/nav tags in backend/main.py
- [x] T016 [P] [US1] Implement extract_title function to get title from title or h1 tags in backend/main.py
- [x] T017 [US1] Implement chunk_text function using LangChain RecursiveCharacterTextSplitter with tiktoken in backend/main.py
- [x] T018 [US1] Implement generate_embeddings function using Cohere batch API with embed-english-v3.0 in backend/main.py
- [x] T019 [US1] Implement initialize_qdrant function to create collection if not exists with 1024-dim COSINE vectors in backend/main.py
- [x] T020 [US1] Implement store_in_qdrant function to upsert points with metadata payload in backend/main.py
- [x] T021 [US1] Implement single-URL processing pipeline: fetch → extract → chunk → embed → store in backend/main.py
- [x] T022 [US1] Add logging for each pipeline stage with timestamps and success/failure status in backend/main.py
- [x] T023 [US1] Create main async function accepting single URL and returning IngestionResult in backend/main.py

**Checkpoint**: Single URL ingestion should be fully functional and independently testable

---

## Phase 4: User Story 2 - Bulk URL Batch Processing (Priority: P2)

**Goal**: Process multiple URLs concurrently with progress tracking and error aggregation

**Independent Test**: Provide list of 10 URLs with 3 intentional failures, verify 7 succeed, 3 logged correctly, processing parallelized, and progress tracked

### Implementation for User Story 2

- [x] T024 [US2] Update main function to accept list of URLs instead of single URL in backend/main.py
- [x] T025 [US2] Implement asyncio.Semaphore(5) concurrency control for rate limiting in backend/main.py
- [x] T026 [US2] Implement process_url_batch function using asyncio.gather with return_exceptions=True in backend/main.py
- [x] T027 [US2] Add tqdm progress bar for batch processing with total/processed/failed counts in backend/main.py
- [x] T028 [US2] Implement error aggregation to collect FailedURL objects with details in backend/main.py
- [x] T029 [US2] Implement deduplication check using Qdrant scroll API to skip existing URLs in backend/main.py
- [x] T030 [US2] Add skip_duplicates parameter to main function with default True in backend/main.py
- [x] T031 [US2] Update IngestionResult to include skipped_count and success_rate property in backend/main.py
- [x] T032 [US2] Add validation to skip URLs returning status_code != 200 or text_length < 50 in backend/main.py

**Checkpoint**: Batch processing should handle multiple URLs with proper error handling and progress tracking

---

## Phase 5: User Story 3 - Configurable Chunking Strategy (Priority: P2)

**Goal**: Allow configuration of chunk sizes and overlap for different content types

**Independent Test**: Configure chunk_size=512/1024/2048 with different overlaps, run on same URL, verify chunks created according to parameters with metadata

### Implementation for User Story 3

- [x] T033 [US3] Add chunk_size parameter to main function with default 512 and validation 128-2048 in backend/main.py
- [x] T034 [US3] Add chunk_overlap parameter to main function with default 50 and validation 0 < overlap < chunk_size in backend/main.py
- [x] T035 [US3] Add embedding_model parameter to main function with default embed-english-v3.0 in backend/main.py
- [x] T036 [US3] Add embedding_dim parameter to main function with default 1024 and validation for valid dimensions in backend/main.py
- [x] T037 [US3] Update chunk_text function to accept configurable chunk_size and chunk_overlap parameters in backend/main.py
- [x] T038 [US3] Store chunking_config snapshot in TextChunk metadata for reproducibility in backend/main.py
- [x] T039 [US3] Add chunk_index and token_count to Qdrant payload metadata in backend/main.py
- [x] T040 [US3] Update initialize_qdrant to use configurable embedding_dim for vector size in backend/main.py
- [x] T041 [US3] Validate embedding_dim matches Qdrant collection configuration on startup in backend/main.py

**Checkpoint**: Chunking strategy should be fully configurable without code changes

---

## Phase 6: User Story 4 - Error Handling and Retry Logic (Priority: P3)

**Goal**: Implement automatic retry logic with exponential backoff for transient failures

**Independent Test**: Simulate Cohere API rate limiting and network failures, verify retries with exponential backoff, persistent failures logged, pipeline completes for non-failing URLs

### Implementation for User Story 4

- [x] T042 [US4] Add max_retries parameter to main function with default 3 and validation 0-5 in backend/main.py
- [x] T043 [US4] Install and configure tenacity library for retry decorators in backend/main.py
- [x] T044 [US4] Apply retry decorator to fetch_url with exponential backoff for network timeouts in backend/main.py
- [x] T045 [US4] Apply retry decorator to generate_embeddings with exponential backoff for Cohere 429/500 errors in backend/main.py
- [x] T046 [US4] Apply retry decorator to store_in_qdrant with exponential backoff for connection errors in backend/main.py
- [x] T047 [US4] Implement error classification: transient vs permanent failures in backend/main.py
- [x] T048 [US4] Add retry_count tracking to FailedURL data class in backend/main.py
- [x] T049 [US4] Add jitter to exponential backoff delays to prevent thundering herd in backend/main.py
- [x] T050 [US4] Log retry attempts with delay duration and error type for observability in backend/main.py
- [x] T051 [US4] Implement timeout configuration for HTTP requests with default 30 seconds in backend/main.py

**Checkpoint**: Pipeline should be resilient to transient failures with automatic recovery

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements affecting all user stories

- [x] T052 [P] Add comprehensive docstrings to all public functions in backend/main.py
- [x] T053 [P] Add type hints to all function signatures and return types in backend/main.py
- [x] T054 Add __name__ == "__main__" entry point for CLI execution in backend/main.py
- [x] T055 [P] Add verbose parameter to control progress bar and detailed logging output in backend/main.py
- [x] T056 Create example usage scripts demonstrating single URL, batch, and custom config in backend/README.md
- [x] T057 [P] Add input validation error messages with actionable guidance in backend/main.py
- [x] T058 Verify all environment variables have fallbacks and clear error messages in backend/main.py
- [x] T059 Add execution_time_seconds tracking to IngestionResult in backend/main.py
- [x] T060 [P] Verify backend/.env.example has all required and optional variables documented in backend/.env.example

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - Can proceed sequentially in priority order (P1 → P2 → P2 → P3)
  - Or in parallel if team capacity allows (after foundational)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends only on Foundational - no dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 (extends single URL to batch)
- **User Story 3 (P2)**: Depends on User Story 1 (adds configuration to existing pipeline)
- **User Story 4 (P3)**: Depends on User Stories 1-3 (adds retry logic to all operations)

### Within Each User Story

- Helper functions can be implemented in parallel (marked [P])
- Pipeline orchestration depends on helper functions
- Logging and validation added after core functionality
- Each story builds incrementally on the previous

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T002, T003 (different files)
- T005 (after T004, but parallel to T006)
- T007 (independent)

**Within Foundational (Phase 2)**:
- T010, T011, T013 (independent utilities)

**Within User Story 1 (Phase 3)**:
- T014, T015, T016 (independent helper functions)

**Within Polish (Phase 7)**:
- T052, T053, T056, T057, T060 (different concerns)

---

## Parallel Example: User Story 1 Core Functions

```bash
# Launch all helper functions for User Story 1 together:
Task: "Implement async fetch_url function using aiohttp"
Task: "Implement extract_text function using BeautifulSoup"
Task: "Implement extract_title function to get title"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013) - CRITICAL
3. Complete Phase 3: User Story 1 (T014-T023)
4. **STOP and VALIDATE**: Test with https://docs.python.org/3/tutorial/index.html
5. Verify embeddings stored in Qdrant and retrievable

### Incremental Delivery

1. Setup + Foundational → Foundation ready (T001-T013)
2. Add User Story 1 → Single URL ingestion works (T014-T023) → MVP! 🎯
3. Add User Story 2 → Batch processing works (T024-T032) → Production-ready
4. Add User Story 3 → Configurable chunking (T033-T041) → Flexible
5. Add User Story 4 → Retry logic (T042-T051) → Resilient
6. Add Polish → Documentation and refinements (T052-T060) → Complete

### Sequential Strategy (Single Developer)

1. Complete phases in order: 1 → 2 → 3 → 4 → 5 → 6 → 7
2. Within each phase, do [P] tasks in parallel where possible
3. Stop at User Story 1 checkpoint for MVP validation
4. Continue to User Story 2 for batch capability
5. Add User Stories 3-4 for production resilience

---

## Notes

- **Single-file implementation**: All code in backend/main.py per user requirements
- **No tests**: Testing not requested in spec, focus on production code only
- **[P] tasks**: Can run in parallel (different files or independent logic)
- **[Story] labels**: Map tasks to user stories for traceability
- **File paths**: All work in backend/main.py except docs in backend/README.md and backend/.env.example
- **Dependencies**: User Stories 2-4 build incrementally on User Story 1
- **Validation checkpoints**: Test each user story independently before moving to next
- **MVP scope**: User Story 1 only (T001-T023) provides end-to-end working pipeline

---

## Task Summary

- **Total tasks**: 60
- **Setup**: 7 tasks
- **Foundational**: 6 tasks
- **User Story 1 (P1 - MVP)**: 10 tasks
- **User Story 2 (P2)**: 9 tasks
- **User Story 3 (P2)**: 9 tasks
- **User Story 4 (P3)**: 10 tasks
- **Polish**: 9 tasks
- **Parallel opportunities**: 14 tasks marked [P]

---

**Generated**: 2025-12-25
**Ready for**: `/sp.implement` command
