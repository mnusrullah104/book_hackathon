"""
Complete cleanup: delete ALL points from Qdrant and re-ingest from correct URLs.
"""

import os
import asyncio
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from ingest_correct_urls import URLS, CORRECT_BASE
from main import main as ingest

load_dotenv()

# Connect to Qdrant
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = "web_documents"

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

print("=" * 60)
print("STEP 1: COMPLETE CLEANUP - DELETE ALL POINTS")
print("=" * 60)

# Get current count
collection_info = client.get_collection(collection_name)
print(f"\nCurrent points in collection: {collection_info.points_count}")

if collection_info.points_count > 0:
    print(f"\nDeleting ALL {collection_info.points_count} points...")

    # Get all point IDs
    all_points, _ = client.scroll(
        collection_name=collection_name,
        limit=10000,  # Get all points
        with_payload=False,
        with_vectors=False
    )

    point_ids = [str(point.id) for point in all_points]

    if point_ids:
        client.delete(
            collection_name=collection_name,
            points_selector=point_ids
        )
        print(f"[SUCCESS] Deleted {len(point_ids)} points")

    # Verify cleanup
    collection_info = client.get_collection(collection_name)
    print(f"Remaining points: {collection_info.points_count}")
else:
    print("Collection already empty")

print(f"\n{'=' * 60}")
print("STEP 2: RE-INGEST FROM CORRECT URLs")
print(f"Base URL: {CORRECT_BASE}")
print(f"{'=' * 60}\n")

print(f"URLs to ingest ({len(URLS)} total):")
for i, url in enumerate(URLS, 1):
    print(f"  {i}. {url}")

print(f"\n{'=' * 60}")
print("STARTING INGESTION")
print(f"{'=' * 60}\n")

async def run_ingestion():
    result = await ingest(
        urls=URLS,
        chunk_size=512,
        chunk_overlap=50,
        batch_size=5,
        skip_duplicates=False,  # No duplicates since we cleaned everything
        verbose=True
    )

    print(f"\n{'=' * 60}")
    print("INGESTION COMPLETE")
    print(f"{'=' * 60}")
    print(f"Success: {result.success_count} URLs")
    print(f"Failed: {result.failed_count} URLs")
    print(f"Skipped: {result.skipped_count} URLs")
    print(f"Total Chunks: {result.total_chunks}")
    print(f"Time: {result.execution_time_seconds:.2f}s")
    print(f"Success Rate: {result.success_rate:.1f}%")

    if result.failed_urls:
        print(f"\nFailed URLs:")
        for failed in result.failed_urls:
            print(f"  - {failed.url}: {failed.error_message}")

    return result

# Run ingestion
result = asyncio.run(run_ingestion())

# Final verification
print(f"\n{'=' * 60}")
print("FINAL VERIFICATION")
print(f"{'=' * 60}")

collection_info = client.get_collection(collection_name)
print(f"\nTotal chunks in collection: {collection_info.points_count}")

# Show all unique URLs
all_points, _ = client.scroll(
    collection_name=collection_name,
    limit=1000,
    with_payload=True,
    with_vectors=False
)

urls = set(point.payload.get("url", "") for point in all_points)
print(f"Unique URLs: {len(urls)}")
print(f"\nStored URLs:")
for i, url in enumerate(sorted(urls), 1):
    print(f"  {i}. {url}")

# Verify all URLs have correct domain
incorrect_urls = [url for url in urls if CORRECT_BASE not in url]
if incorrect_urls:
    print(f"\n[WARNING] Found {len(incorrect_urls)} URLs with incorrect domain:")
    for url in incorrect_urls:
        print(f"  - {url}")
else:
    print(f"\n[SUCCESS] All URLs use correct domain: {CORRECT_BASE}")

print("\n" + "=" * 60)
print("[COMPLETE] Cleanup and re-ingestion finished")
print("=" * 60)
