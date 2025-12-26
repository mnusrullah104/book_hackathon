"""
Check what's currently stored in Qdrant collection.
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

# Get collection info
try:
    collection_info = client.get_collection(collection_name)
    print(f"\n{'='*60}")
    print(f"QDRANT COLLECTION: {collection_name}")
    print(f"{'='*60}")
    print(f"Vector Size: {collection_info.config.params.vectors.size}")
    print(f"Distance: {collection_info.config.params.vectors.distance}")
    print(f"Total Points: {collection_info.points_count}")
    print(f"Status: {collection_info.status}")

    # Get all unique URLs
    results, _ = client.scroll(
        collection_name=collection_name,
        limit=1000,
        with_payload=True,
        with_vectors=False
    )

    urls = set()
    for point in results:
        if 'url' in point.payload:
            urls.add(point.payload['url'])

    print(f"\n{'='*60}")
    print(f"STORED URLs ({len(urls)} unique):")
    print(f"{'='*60}")
    for i, url in enumerate(sorted(urls), 1):
        # Count chunks per URL
        url_results, _ = client.scroll(
            collection_name=collection_name,
            scroll_filter={
                "must": [
                    {"key": "url", "match": {"value": url}}
                ]
            },
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        print(f"{i}. {url} ({len(url_results)} chunks)")

    print(f"\n{'='*60}")
    print(f"Total URLs: {len(urls)}")
    print(f"Total Chunks: {collection_info.points_count}")
    print(f"{'='*60}\n")

except Exception as e:
    print(f"Error: {e}")
