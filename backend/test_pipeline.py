"""
Test script for the web embedding ingestion pipeline.
Demonstrates single URL and batch processing.
"""

import asyncio
from main import main

async def test_single_url():
    """Test single URL ingestion."""
    print("=" * 60)
    print("TEST 1: Single URL Ingestion")
    print("=" * 60)

    result = await main(
        urls=["https://docs.python.org/3/tutorial/introduction.html"],
        verbose=True
    )

    print(f"\nRESULTS:")
    print(f"   Success: {result.success_count}/{result.success_count + result.failed_count}")
    print(f"   Chunks: {result.total_chunks}")
    print(f"   Time: {result.execution_time_seconds:.2f}s")
    print(f"   Success Rate: {result.success_rate:.1f}%")


async def test_batch_processing():
    """Test batch URL ingestion."""
    print("\n" + "=" * 60)
    print("TEST 2: Batch URL Processing")
    print("=" * 60)

    urls = [
        "https://www.python.org/about/",
        "https://www.python.org/about/success/",
        "https://www.python.org/about/apps/",
    ]

    result = await main(
        urls=urls,
        chunk_size=512,
        batch_size=3,
        skip_duplicates=True,
        verbose=True
    )

    print(f"\nRESULTS:")
    print(f"   Success: {result.success_count}")
    print(f"   Failed: {result.failed_count}")
    print(f"   Skipped: {result.skipped_count}")
    print(f"   Total Chunks: {result.total_chunks}")
    print(f"   Time: {result.execution_time_seconds:.2f}s")
    print(f"   Success Rate: {result.success_rate:.1f}%")

    if result.failed_urls:
        print(f"\nFAILED URLs:")
        for failed in result.failed_urls:
            print(f"   - {failed.url}: {failed.error_message}")


async def test_custom_config():
    """Test with custom chunking configuration."""
    print("\n" + "=" * 60)
    print("TEST 3: Custom Configuration (Larger Chunks)")
    print("=" * 60)

    result = await main(
        urls=["https://www.python.org/downloads/"],
        chunk_size=1024,  # Larger chunks
        chunk_overlap=100,  # More overlap
        skip_duplicates=False,  # Re-ingest even if exists
        verbose=True
    )

    print(f"\nRESULTS:")
    print(f"   Success: {result.success_count}")
    print(f"   Chunks: {result.total_chunks}")
    print(f"   Time: {result.execution_time_seconds:.2f}s")


async def main_test():
    """Run all tests."""
    print("\n[STARTING] Pipeline Tests\n")

    # Test 1: Single URL
    await test_single_url()

    # Test 2: Batch processing
    await test_batch_processing()

    # Test 3: Custom configuration
    await test_custom_config()

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main_test())
