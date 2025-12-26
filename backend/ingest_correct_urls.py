"""
Ingest documentation from CORRECT URLs (book-hackathon-blond.vercel.app).
Manually constructs URL list to bypass sitemap caching issues.
"""

import asyncio
from main import main as ingest

# Correct base URL
CORRECT_BASE = "https://book-hackathon-blond.vercel.app"

# All documentation URLs (manually constructed from structure)
URLS = [
    f"{CORRECT_BASE}/",
    f"{CORRECT_BASE}/about",
    f"{CORRECT_BASE}/docs/",
    f"{CORRECT_BASE}/docs/module-1/ros2-fundamentals",
    f"{CORRECT_BASE}/docs/module-1/python-agents-rclpy",
    f"{CORRECT_BASE}/docs/module-1/humanoid-urdf",
    f"{CORRECT_BASE}/docs/module-2/2.1-physics-simulation-gazebo",
    f"{CORRECT_BASE}/docs/module-2/2.2-environment-unity",
    f"{CORRECT_BASE}/docs/module-2/2.3-sensor-simulation",
    f"{CORRECT_BASE}/docs/isaac-robot-brain/",
    f"{CORRECT_BASE}/docs/isaac-robot-brain/3.1-chapter-1-isaac-sim-fundamentals",
    f"{CORRECT_BASE}/docs/isaac-robot-brain/3.2-chapter-2-isaac-ros-perception-vslam",
    f"{CORRECT_BASE}/docs/isaac-robot-brain/3.3-chapter-3-navigation-with-nav2-humanoids",
    f"{CORRECT_BASE}/docs/vla-integration/",
    f"{CORRECT_BASE}/docs/vla-integration/4.1-chapter-1-voice-to-action-pipelines",
    f"{CORRECT_BASE}/docs/vla-integration/4.2-chapter-2-cognitive-planning-with-llms",
    f"{CORRECT_BASE}/docs/vla-integration/4.3-chapter-3-capstone-autonomous-humanoid",
]

async def main():
    print("=" * 60)
    print("INGESTING FROM CORRECT URLs")
    print(f"Base URL: {CORRECT_BASE}")
    print("=" * 60)
    print(f"\nURLs to ingest ({len(URLS)} total):")
    for i, url in enumerate(URLS, 1):
        print(f"  {i}. {url}")

    print(f"\n{'=' * 60}")
    print("STARTING INGESTION")
    print(f"{'=' * 60}\n")

    result = await ingest(
        urls=URLS,
        chunk_size=512,
        chunk_overlap=50,
        batch_size=5,
        skip_duplicates=True,
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

    print(f"\n{'=' * 60}")
    print("[SUCCESS] Documentation ingested with CORRECT URLs")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    asyncio.run(main())
