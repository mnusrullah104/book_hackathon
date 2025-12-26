# Quickstart: RAG Retrieval Validation and Testing

**Feature**: 003-rag-retrieval-validation
**Estimated Time**: 10-15 minutes
**Prerequisites**: Completed ingestion pipeline (002-web-embedding-ingestion), API keys configured

## Overview

This guide walks you through testing the RAG retrieval pipeline to verify that:
1. Vector search retrieves correct, relevant chunks
2. Metadata is complete and accurate
3. End-to-end ingestion → retrieval flow works
4. Embedding dimensions and consistency are validated

## Step 1: Verify Prerequisites (2 minutes)

### Check Environment Setup

```bash
cd backend

# Verify .env file exists with API keys
cat .env | grep -E "(COHERE_API_KEY|QDRANT_URL|QDRANT_API_KEY)"

# Expected output: Your actual API keys (not "your-api-key-here")
```

### Verify Qdrant Collection

```python
# Run check_qdrant.py to see what's stored
python check_qdrant.py
```

**Expected Output**:
```
QDRANT COLLECTION: web_documents
Total Points: 109
Total URLs: 22
```

If collection is empty or doesn't exist, run the ingestion pipeline first:
```bash
python ingest_from_sitemap.py
```

---

## Step 2: Run Basic Retrieval Test (3 minutes)

### Test Query 1: Module 1 Content

```python
# Create test file: test_query.py
import asyncio
from retrieve import search

async def test():
    result = await search(
        "How do I set up ROS 2 for humanoid robots?",
        top_k=5,
        score_threshold=0.7
    )

    print(f"Found {result.total_results} chunks")
    for i, chunk in enumerate(result.chunks, 1):
        print(f"{i}. [{chunk.similarity_score:.3f}] {chunk.title}")

asyncio.run(test())
```

**Expected Behavior**:
- Returns 5 chunks (or fewer if score_threshold filters some)
- Top results from Module 1 (ROS 2 Fundamentals, Python Agents, URDF)
- Similarity scores > 0.7
- Each chunk has complete metadata (url, title, chunk_text)

---

## Step 3: Test Metadata Filtering (2 minutes)

### Filter by Module

```python
# Test filtering for Module 3 only
result = await search(
    "NVIDIA Isaac Sim for robot simulation",
    url_filter="isaac-robot-brain",
    top_k=3
)

# Verify all results are from Module 3
for chunk in result.chunks:
    assert "isaac-robot-brain" in chunk.url
    print(f"✓ {chunk.title}")
```

**Expected Behavior**:
- Only chunks from Module 3 (Isaac-related pages)
- No chunks from Modules 1, 2, or 4
- Similarity scores reflect relevance within filtered set

---

## Step 4: Run End-to-End Test (4 minutes)

### Ingest → Retrieve Flow

```python
# Test end-to-end pipeline
import asyncio
from main import main as ingest
from retrieve import search

async def e2e_test():
    # Ingest a small test URL
    test_url = "https://www.python.org/about/gettingstarted/"

    print("1. Ingesting test URL...")
    ingest_result = await ingest([test_url], skip_duplicates=False)
    print(f"   Ingested {ingest_result.total_chunks} chunks")

    # Query for content from test URL
    print("\n2. Querying for test content...")
    result = await search("getting started with Python", top_k=5)

    # Verify test chunks are retrievable
    test_chunks = [c for c in result.chunks if test_url in c.url]
    print(f"   Found {len(test_chunks)} chunks from test URL")

    # Assertions
    assert len(test_chunks) > 0, "Test URL not found in results"
    assert test_chunks[0].similarity_score > 0.8, "Low similarity"

    print("\n✓ End-to-end test PASSED")

asyncio.run(e2e_test())
```

**Expected Behavior**:
- Test URL ingested successfully
- Query retrieves chunks from test URL
- High similarity (>0.8) for relevant query
- All metadata fields present

---

## Step 5: Run Validation Suite (3 minutes)

### Automated Checks

```python
# Run comprehensive validation
from retrieve import validate_pipeline

result = await validate_pipeline(verbose=True)

print(f"\nValidation Status: {result.status}")
print(f"Checks Passed: {result.passed_checks}/{result.total_checks}")
```

**Expected Output**:
```
=== RAG Pipeline Validation ===

[DIMENSION CHECK] PASS
  All 109+ vectors have 1024 dimensions

[METADATA CHECK] PASS
  All chunks have required fields

[SIMILARITY CHECK] PASS
  Identical text similarity: 0.998

[DUPLICATE CHECK] PASS
  No unintentional duplicates found

=== SUMMARY ===
Status: PASS
Checks: 4/4 passed
```

---

## Step 6: Run Sample Queries (2 minutes)

### Test Different Modules

```python
# Test queries across all 4 modules
queries = [
    ("How do I create a ROS 2 node?", "Module 1"),
    ("Gazebo physics simulation setup", "Module 2"),
    ("Isaac ROS perception packages", "Module 3"),
    ("Voice to action pipeline with LLMs", "Module 4")
]

for query_text, expected_module in queries:
    result = await search(query_text, top_k=3)
    print(f"\nQuery: {query_text}")
    print(f"Expected: {expected_module}")
    print(f"Top Result: {result.chunks[0].title}")
    print(f"Similarity: {result.chunks[0].similarity_score:.3f}")
```

**Expected Behavior**:
- Each query returns chunks from the expected module
- Similarity scores > 0.7 for well-matched queries
- Results ordered by relevance

---

## Common Issues & Solutions

### Issue 1: Empty Results

**Symptom**: Query returns 0 chunks or very low similarity (<0.5)

**Solutions**:
- Check if collection has relevant content: `python check_qdrant.py`
- Lower `score_threshold` to 0.0 to see all results
- Try more specific or different query phrasing
- Verify ingestion completed successfully

### Issue 2: Metadata Missing

**Symptom**: Retrieved chunks missing url, title, or other fields

**Solutions**:
- Run validation: `await validate_pipeline()`
- Check ingestion logs for errors
- Verify Qdrant collection schema matches ingestion

### Issue 3: Low Similarity Scores

**Symptom**: Relevant content has similarity <0.6

**Solutions**:
- Verify using same Cohere model (embed-english-v3.0)
- Check query phrasing (try more specific keywords)
- Inspect chunk_text to see what was actually ingested
- This may be normal for loosely related content

### Issue 4: Connection Errors

**Symptom**: QdrantConnectionError or CohereAPIError

**Solutions**:
- Verify .env has correct API keys
- Test Qdrant connection: `python check_qdrant.py`
- Check API key quotas/limits
- Verify network connectivity

---

## Verification Checklist

After completing this quickstart, verify:

- [ ] Basic search returns relevant results in <1s
- [ ] Top similarity scores >0.7 for module-matching queries
- [ ] All retrieved chunks have complete metadata
- [ ] URL filtering returns only chunks from specified module
- [ ] End-to-end test (ingest → retrieve) passes
- [ ] Validation suite shows 100% pass rate
- [ ] Sample queries across all 4 modules return expected content

**If all items checked**: RAG retrieval pipeline is fully validated and operational! ✅

---

## Next Steps

1. **Integrate with Agent**: Import `search()` function in agent code
2. **Add to FastAPI**: Create `/api/search` endpoint using `search()`
3. **Optimize**: Add caching for frequent queries
4. **Monitor**: Track query patterns and similarity distributions

---

## Reference

- **Specification**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Data Model**: [data-model.md](data-model.md)
- **Python Interface**: [contracts/python-interface.md](contracts/python-interface.md)
