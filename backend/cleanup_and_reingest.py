"""
Clean up old URLs and re-ingest from correct sitemap.
Removes: book-writing-hackathon1.vercel.app URLs
Removes: Python.org test URLs
Keeps: Only book-hackathon-blond.vercel.app URLs
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from bs4 import BeautifulSoup
from main import main as ingest

load_dotenv()

# Connect to Qdrant
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = "web_documents"

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

print("="*60)
print("STEP 1: CLEANING UP OLD URLs FROM QDRANT")
print("="*60)

# Patterns to remove
patterns_to_remove = [
    "book-writing-hackathon1.vercel.app",
    "docs.python.org",
    "www.python.org"
]

total_deleted = 0

for pattern in patterns_to_remove:
    print(f"\nSearching for: {pattern}")

    # Get all points (no filter needed, we'll filter in Python)
    all_points, _ = client.scroll(
        collection_name=collection_name,
        limit=1000,
        with_payload=True
    )

    # Filter by URL pattern in Python
    points_to_delete = []
    for point in all_points:
        url = point.payload.get("url", "")
        if pattern in url:
            points_to_delete.append(str(point.id))

    if points_to_delete:
        print(f"  Found {len(points_to_delete)} chunks to delete")
        client.delete(
            collection_name=collection_name,
            points_selector=points_to_delete
        )
        total_deleted += len(points_to_delete)
        print(f"  Deleted {len(points_to_delete)} chunks")
    else:
        print(f"  No chunks found with pattern: {pattern}")

print(f"\n{'='*60}")
print(f"Total deleted: {total_deleted} chunks")
print(f"{'='*60}")

# Check remaining
collection_info = client.get_collection(collection_name)
print(f"\nRemaining chunks: {collection_info.points_count}")

print(f"\n{'='*60}")
print("STEP 2: RE-INGESTING FROM CORRECT SITEMAP")
print(f"{'='*60}\n")

async def fetch_and_ingest():
    """Fetch correct sitemap and ingest all URLs."""
    correct_url = "https://book-hackathon-blond.vercel.app"
    sitemap_url = f"{correct_url}/sitemap.xml"

    print(f"Fetching sitemap from: {sitemap_url}\n")

    # Fetch sitemap
    async with aiohttp.ClientSession() as session:
        async with session.get(sitemap_url) as response:
            if response.status != 200:
                print(f"Failed to fetch sitemap: HTTP {response.status}")
                return

            content = await response.text()

    # Parse sitemap
    soup = BeautifulSoup(content, 'xml')
    urls = [loc.text.strip() for loc in soup.find_all('loc') if loc.text.strip()]

    print(f"Found {len(urls)} URLs in sitemap")
    print(f"\nURLs to ingest:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")

    print(f"\n{'='*60}")
    print("INGESTING DOCUMENTATION")
    print(f"{'='*60}\n")

    # Ingest all URLs
    result = await ingest(
        urls=urls,
        chunk_size=512,
        chunk_overlap=50,
        batch_size=5,
        skip_duplicates=True,
        verbose=True
    )

    print(f"\n{'='*60}")
    print("INGESTION COMPLETE")
    print(f"{'='*60}")
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

    print(f"\n{'='*60}")
    print("[SUCCESS] ALL DOCUMENTATION RE-INGESTED")
    print(f"{'='*60}\n")

# Run ingestion
asyncio.run(fetch_and_ingest())

# Final verification
print("="*60)
print("FINAL VERIFICATION")
print("="*60)

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

print("\n" + "="*60)
print("[COMPLETE] Cleanup and re-ingestion finished")
print("="*60)
