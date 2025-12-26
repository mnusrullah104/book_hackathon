"""
Test script for RAG retrieval and validation.
Demonstrates sample queries and automated validation checks.
"""

import asyncio
from retrieve import search, RetrievalResult


# =============================================================================
# USER STORY 1: BASIC VECTOR SEARCH TESTS
# =============================================================================

async def test_module1_query():
    """Test query for Module 1 (ROS 2) content."""
    print("="*60)
    print("TEST 1: Module 1 Query (ROS 2 Fundamentals)")
    print("="*60)

    result = await search(
        "How do I set up ROS 2 for humanoid robots?",
        top_k=5,
        score_threshold=0.0,  # No threshold, show all results
        verbose=False
    )

    print(f"\nQuery: {result.query}")
    print(f"Results: {result.total_results}")
    print(f"Top Score: {result.top_score:.3f}")
    print(f"Avg Score: {result.avg_score:.3f}")
    print(f"Time: {result.execution_time_seconds:.3f}s")

    print(f"\nTop {min(3, len(result.chunks))} Results:")
    for i, chunk in enumerate(result.chunks[:3], 1):
        print(f"\n{i}. [{chunk.similarity_score:.3f}] {chunk.title}")
        print(f"   URL: {chunk.url}")
        print(f"   Chunk {chunk.chunk_index}: {chunk.chunk_text[:100]}...")

    # Assertions
    assert result.total_results > 0, "No results returned"
    assert result.top_score >= 0.5, f"Very low similarity: {result.top_score}"
    assert any("module-1" in c.url or "ros" in c.url.lower() for c in result.chunks), "No Module 1 content in results"

    print(f"\n[PASS] Test PASSED")
    return result


async def test_module3_query():
    """Test query for Module 3 (NVIDIA Isaac) content."""
    print("\n" + "="*60)
    print("TEST 2: Module 3 Query (NVIDIA Isaac Sim)")
    print("="*60)

    result = await search(
        "NVIDIA Isaac Sim for robot simulation and perception",
        top_k=5,
        score_threshold=0.0,
        verbose=False
    )

    print(f"\nQuery: {result.query}")
    print(f"Results: {result.total_results}")
    print(f"Top Score: {result.top_score:.3f}")

    print(f"\nTop Results:")
    for i, chunk in enumerate(result.chunks[:3], 1):
        print(f"{i}. [{chunk.similarity_score:.3f}] {chunk.title}")

    # Assertions
    assert result.total_results > 0, "No results returned"
    assert any("isaac" in c.url.lower() for c in result.chunks), "No Isaac content in results"

    print(f"\n[PASS] Test PASSED")
    return result


async def test_module4_query():
    """Test query for Module 4 (VLA) content."""
    print("\n" + "="*60)
    print("TEST 3: Module 4 Query (Vision-Language-Action)")
    print("="*60)

    result = await search(
        "voice to action pipeline with LLMs for autonomous robots",
        top_k=5,
        score_threshold=0.0,
        verbose=False
    )

    print(f"\nQuery: {result.query}")
    print(f"Results: {result.total_results}")
    print(f"Top Score: {result.top_score:.3f}")

    print(f"\nTop Results:")
    for i, chunk in enumerate(result.chunks[:3], 1):
        print(f"{i}. [{chunk.similarity_score:.3f}] {chunk.title}")

    # Assertions
    assert result.total_results > 0, "No results returned"
    assert any("vla" in c.url.lower() or "4." in c.url for c in result.chunks), "No VLA content in results"

    print(f"\n[PASS] Test PASSED")
    return result


# =============================================================================
# PLACEHOLDER FOR PHASE 4-6 TESTS
# =============================================================================

# TODO: Phase 4 - User Story 2 tests (metadata filtering)
# TODO: Phase 5 - User Story 3 tests (end-to-end)
# TODO: Phase 6 - User Story 4 tests (validation suite)


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_all_tests():
    """Run all retrieval tests."""
    print("\n" + "="*60)
    print("[STARTING] RAG Retrieval Tests")
    print("="*60 + "\n")

    try:
        # Phase 3: Basic retrieval tests
        await test_module1_query()
        await test_module3_query()
        await test_module4_query()

        # TODO: Phase 4-6 tests will be added here

        print("\n" + "="*60)
        print("[SUCCESS] All Tests Passed")
        print("="*60 + "\n")

    except AssertionError as e:
        print(f"\n[FAILED] Test assertion failed: {e}")
        raise
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
