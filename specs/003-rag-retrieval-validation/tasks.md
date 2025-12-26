---
description: "Implementation tasks for RAG Retrieval Validation and Testing"
---

# Tasks: RAG Retrieval Validation and Testing

**Feature**: 003-rag-retrieval-validation
**Input**: Design documents from `/specs/003-rag-retrieval-validation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Minimal validation tests included per spec (assertion-based, not comprehensive)

**Organization**: Tasks organized by user story to enable independent implementation and testing

## Format: `- [ ] [ID] [P?] [Story] Description`

- **Checkbox**: `- [ ]` (markdown checkbox)
- **[ID]**: Sequential task number (T001, T002, etc.)
- **[P]**: Task can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4) - only for user story phases
- **Description**: Clear action with exact file path

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Verify existing setup and prepare for retrieval implementation

- [x] T001 Verify backend/.env has COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY configured
- [x] T002 Verify Qdrant collection web_documents exists with 109+ chunks via check_qdrant.py
- [x] T003 Verify all required dependencies installed (cohere, qdrant-client, python-dotenv) in backend/requirements.txt

---

## Phase 2: Foundational (Core Infrastructure)

**Purpose**: Shared data classes and utilities for retrieval and validation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create RetrievedChunk data class with all metadata fields in backend/retrieve.py
- [x] T005 Create RetrievalResult data class with query, chunks, stats in backend/retrieve.py
- [x] T006 Create ValidationReport data class with test results in backend/retrieve.py
- [x] T007 [P] Import exception types from main.py: ConfigurationError, QdrantConnectionError, CohereAPIError in backend/retrieve.py
- [x] T008 [P] Implement config loading function with env var fallbacks for Cohere and Qdrant in backend/retrieve.py
- [x] T009 [P] Setup logging configuration consistent with main.py in backend/retrieve.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Basic Vector Search Retrieval (Priority: P1) 🎯 MVP

**Goal**: Query Qdrant with text, retrieve relevant chunks with similarity scores

**Independent Test**: Query "How do I set up ROS 2 for humanoids?", verify Module 1 chunks returned with >0.7 similarity

### Implementation for User Story 1

- [x] T010 [P] [US1] Implement async embed_query function using Cohere with search_query input type in backend/retrieve.py
- [x] T011 [US1] Implement async search_qdrant function using client.search() with COSINE distance in backend/retrieve.py
- [x] T012 [US1] Implement parse_search_results function to convert ScoredPoint to RetrievedChunk in backend/retrieve.py
- [x] T013 [US1] Implement main search function accepting query_text and top_k parameters in backend/retrieve.py
- [x] T014 [US1] Add input validation for query_text (not empty) and top_k (1-100) in backend/retrieve.py
- [x] T015 [US1] Add logging for query text, result count, and top similarity scores in backend/retrieve.py
- [x] T016 [US1] Calculate and populate top_score and avg_score in RetrievalResult in backend/retrieve.py
- [x] T017 [US1] Create test_retrieval.py with sample query for Module 1 content in backend/test_retrieval.py
- [x] T018 [US1] Add CLI entry point for running test queries in backend/retrieve.py

**Checkpoint**: Basic vector search functional and independently testable

---

## Phase 4: User Story 2 - Metadata Validation and Filtering (Priority: P2)

**Goal**: Retrieve complete metadata and filter results by URL patterns

**Independent Test**: Query with url_filter="module-2", verify only Module 2 chunks returned with complete metadata

### Implementation for User Story 2

- [ ] T019 [US2] Add url_filter parameter to search function in backend/retrieve.py
- [ ] T020 [US2] Implement Qdrant Filter for URL pattern matching using MatchText in backend/retrieve.py
- [ ] T021 [US2] Add score_threshold parameter to filter low-relevance results in backend/retrieve.py
- [ ] T022 [US2] Implement validate_metadata function checking required fields (url, chunk_text, timestamp, chunk_index) in backend/retrieve.py
- [ ] T023 [US2] Add metadata validation to parse_search_results function in backend/retrieve.py
- [ ] T024 [US2] Add test for URL filtering by module in backend/test_retrieval.py
- [ ] T025 [US2] Add test verifying all chunks have complete metadata in backend/test_retrieval.py

**Checkpoint**: Metadata filtering and validation working correctly

---

## Phase 5: User Story 3 - Ingestion-to-Retrieval End-to-End Test (Priority: P2)

**Goal**: Validate full pipeline from ingestion through retrieval

**Independent Test**: Ingest test URL, query for its content, verify retrieval with >0.95 similarity

### Implementation for User Story 3

- [ ] T026 [US3] Create end_to_end_test function that imports main.py ingest function in backend/test_retrieval.py
- [ ] T027 [US3] Implement test URL ingestion with unique content keyword in backend/test_retrieval.py
- [ ] T028 [US3] Implement query for test content after ingestion completes in backend/test_retrieval.py
- [ ] T029 [US3] Add assertion verifying test chunks retrievable with >0.95 similarity in backend/test_retrieval.py
- [ ] T030 [US3] Add cleanup option to delete test chunks after validation in backend/test_retrieval.py
- [ ] T031 [US3] Add consistency test: embed same text twice, verify >0.99 similarity in backend/test_retrieval.py

**Checkpoint**: End-to-end pipeline validation working

---

## Phase 6: User Story 4 - Consistency and Correctness Validation (Priority: P3)

**Goal**: Automated assertions for dimensions, metadata, and consistency

**Independent Test**: Run validation suite, verify 100% pass rate on all checks

### Implementation for User Story 4

- [ ] T032 [P] [US4] Implement validate_dimensions function checking all vectors are 1024-dim in backend/retrieve.py
- [ ] T033 [P] [US4] Implement validate_metadata_completeness function checking required fields in backend/retrieve.py
- [ ] T034 [P] [US4] Implement validate_embedding_consistency function testing identical text similarity in backend/retrieve.py
- [ ] T035 [US4] Implement validate_pipeline function orchestrating all validation checks in backend/retrieve.py
- [ ] T036 [US4] Create ValidationReport object with pass/fail status and issue details in backend/retrieve.py
- [ ] T037 [US4] Add validation test script running all checks and displaying report in backend/test_retrieval.py
- [ ] T038 [US4] Add CLI entry point for validation in backend/retrieve.py

**Checkpoint**: Automated validation suite functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, examples, and final refinements

- [ ] T039 [P] Add comprehensive docstrings to all public functions in backend/retrieve.py
- [ ] T040 [P] Add type hints to all function signatures and return types in backend/retrieve.py
- [ ] T041 Add __name__ == "__main__" entry point for CLI testing in backend/retrieve.py
- [ ] T042 [P] Create sample_queries.py with queries for all 4 modules in backend/sample_queries.py
- [ ] T043 Update backend/README.md with retrieval examples and usage instructions in backend/README.md
- [ ] T044 [P] Add error handling for empty results (return empty list gracefully) in backend/retrieve.py
- [ ] T045 Add include_vectors parameter to optionally return embeddings in backend/retrieve.py
- [ ] T046 Add execution_time_seconds tracking to RetrievalResult in backend/retrieve.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - Can proceed sequentially in priority order (P1 → P2 → P2 → P3)
  - Or in parallel if independent (US1 and US4 are independent)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends only on Foundational - no dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 (adds filtering to basic search)
- **User Story 3 (P2)**: Depends on User Story 1 (uses search function for E2E test)
- **User Story 4 (P3)**: Independent of other stories (direct Qdrant validation)

### Within Each User Story

- Helper functions can be implemented in parallel (marked [P])
- Main orchestration depends on helpers
- Test scripts added after implementation
- Each story builds incrementally

### Parallel Opportunities

**Within Foundational (Phase 2)**:
- T007, T008, T009 (independent utilities)

**Within User Story 1 (Phase 3)**:
- T010 (independent helper function)

**Within User Story 4 (Phase 6)**:
- T032, T033, T034 (independent validation functions)

**Within Polish (Phase 7)**:
- T039, T040, T042, T044 (different concerns)

---

## Parallel Example: User Story 1 Core Functions

```bash
# Launch helper function for User Story 1:
Task: "Implement async embed_query function using Cohere"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003) - Verification
2. Complete Phase 2: Foundational (T004-T009) - Data classes and config
3. Complete Phase 3: User Story 1 (T010-T018) - Basic search
4. **STOP and VALIDATE**: Query "ROS 2 fundamentals", verify relevant results
5. Test across all 4 modules

### Incremental Delivery

1. Setup + Foundational → Foundation ready (T001-T009)
2. Add User Story 1 → Basic search works (T010-T018) → MVP! 🎯
3. Add User Story 2 → Filtering works (T019-T025) → Enhanced
4. Add User Story 3 → E2E testing (T026-T031) → Validated
5. Add User Story 4 → Automated validation (T032-T038) → Production-ready
6. Add Polish → Documentation complete (T039-T046) → Complete

### Sequential Strategy (Single Developer)

1. Complete phases in order: 1 → 2 → 3 → 4 → 5 → 6 → 7
2. Within each phase, do [P] tasks in parallel where possible
3. Stop at User Story 1 checkpoint for MVP validation
4. Continue to User Stories 2-3 for filtering and E2E testing
5. Add User Story 4 for automated validation

---

## Notes

- **Single-file implementation**: All code in backend/retrieve.py per user requirements
- **Minimal tests**: Assertion-based validation in test_retrieval.py (not pytest framework)
- **[P] tasks**: Can run in parallel (different files or independent logic)
- **[Story] labels**: Map tasks to user stories for traceability
- **File paths**: Main work in backend/retrieve.py, tests in backend/test_retrieval.py
- **Dependencies**: User Stories 2-3 build on User Story 1, User Story 4 is independent
- **Validation checkpoints**: Test each user story independently before moving to next
- **MVP scope**: User Story 1 only (T001-T018) provides working vector search

---

## Task Summary

- **Total tasks**: 46
- **Setup**: 3 tasks
- **Foundational**: 6 tasks
- **User Story 1 (P1 - MVP)**: 9 tasks
- **User Story 2 (P2)**: 7 tasks
- **User Story 3 (P2)**: 6 tasks
- **User Story 4 (P3)**: 7 tasks
- **Polish**: 8 tasks
- **Parallel opportunities**: 9 tasks marked [P]

---

**Generated**: 2025-12-25
**Ready for**: `/sp.implement` command
