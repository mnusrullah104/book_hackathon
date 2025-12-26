"""
Clean up old URLs from Qdrant and re-ingest from correct sitemap.
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

# Connect to Qdrant
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = "web_documents"

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

print("="*60)
print("CLEANING UP OLD URLs FROM QDRANT")
print("="*60)

# Old URL pattern to remove
old_url_pattern = "book-writing-hackathon1.vercel.app"

# Get all points with old URL pattern
print(f"\nSearching for URLs containing: {old_url_pattern}")

results, _ = client.scroll(
    collection_name=collection_name,
    scroll_filter={
        "must": [
            {"key": "url", "match": {"text": old_url_pattern}}
        ]
    },
    limit=1000,
    with_payload=True
)

print(f"Found {len(results)} chunks with old URL pattern")

if results:
    # Delete all old URL chunks
    point_ids = [str(point.id) for point in results]

    print(f"\nDeleting {len(point_ids)} old chunks...")
    client.delete(
        collection_name=collection_name,
        points_selector=point_ids
    )

    print(f"✓ Deleted {len(point_ids)} chunks with old URLs")

# Also delete Python.org test URLs (keep only book documentation)
python_urls = ["docs.python.org", "www.python.org"]
for pattern in python_urls:
    results, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter={
            "must": [
                {"key": "url", "match": {"text": pattern}}
            ]
        },
        limit=1000,
        with_payload=True
    )

    if results:
        point_ids = [str(point.id) for point in results]
        print(f"\nDeleting {len(point_ids)} test chunks from {pattern}...")
        client.delete(
            collection_name=collection_name,
            points_selector=point_ids
        )

print("\n" + "="*60)
print("CLEANUP COMPLETE")
print("="*60)

# Show final stats
collection_info = client.get_collection(collection_name)
print(f"\nRemaining chunks in collection: {collection_info.points_count}")
print("\nRun: python ingest_from_sitemap.py")
print("To re-ingest from correct URL: https://book-hackathon-blond.vercel.app/sitemap.xml")
