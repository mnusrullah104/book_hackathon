"""
Fetch URLs from sitemap.xml and ingest all documentation.
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from main import main
import os
from dotenv import load_dotenv

load_dotenv()

async def fetch_sitemap_urls(sitemap_url: str):
    """Fetch all URLs from sitemap.xml."""
    print(f"Fetching sitemap from: {sitemap_url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(sitemap_url) as response:
            if response.status != 200:
                print(f"Failed to fetch sitemap: HTTP {response.status}")
                return []

            content = await response.text()

    # Parse sitemap XML
    soup = BeautifulSoup(content, 'xml')

    # Extract all <loc> tags (URLs)
    urls = []
    for loc in soup.find_all('loc'):
        url = loc.text.strip()
        if url:
            urls.append(url)

    print(f"Found {len(urls)} URLs in sitemap")
    return urls

async def main_ingest():
    """Main function to ingest all URLs from sitemap."""

    # Get deployed URL from environment
    deploy_url = os.getenv("Deploy_Vercel_URL", "https://book-hackathon-blond.vercel.app")
    sitemap_url = f"{deploy_url}/sitemap.xml"

    print("="*60)
    print("INGESTING DOCUMENTATION FROM SITEMAP")
    print("="*60)
    print(f"Source: {sitemap_url}")
    print()

    # Fetch all URLs from sitemap
    urls = await fetch_sitemap_urls(sitemap_url)

    if not urls:
        print("No URLs found in sitemap!")
        return

    print(f"\n{'='*60}")
    print(f"URLs TO INGEST ({len(urls)}):")
    print(f"{'='*60}")
    for i, url in enumerate(urls, 1):
        print(f"{i}. {url}")

    print(f"\n{'='*60}")
    print("STARTING BATCH INGESTION")
    print(f"{'='*60}\n")

    # Ingest all URLs with batch processing
    result = await main(
        urls=urls,
        chunk_size=512,
        chunk_overlap=50,
        batch_size=5,  # Process 5 URLs concurrently
        skip_duplicates=True,  # Skip already-ingested URLs
        verbose=True
    )

    print(f"\n{'='*60}")
    print("INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"Success: {result.success_count} URLs")
    print(f"Failed: {result.failed_count} URLs")
    print(f"Skipped: {result.skipped_count} URLs (already in Qdrant)")
    print(f"Total Chunks: {result.total_chunks}")
    print(f"Time: {result.execution_time_seconds:.2f}s")
    print(f"Success Rate: {result.success_rate:.1f}%")

    if result.failed_urls:
        print(f"\n{'='*60}")
        print("FAILED URLs:")
        print(f"{'='*60}")
        for failed in result.failed_urls:
            print(f"- {failed.url}")
            print(f"  Error: {failed.error_message}")
            print(f"  Type: {failed.error_type}")

    print(f"\n{'='*60}")
    print(f"✓ ALL DOCUMENTATION INGESTED TO QDRANT")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main_ingest())
