# Quickstart: Website URL Embedding Ingestion Pipeline

**Feature**: 002-web-embedding-ingestion
**Date**: 2025-12-24
**Time to Complete**: 15-30 minutes

## Overview

This guide walks you through setting up and running the website URL embedding ingestion pipeline from scratch. By the end, you'll have ingested your first website and verified the embeddings are stored in Qdrant.

## Prerequisites

- **Python 3.9+** installed
- **UV package manager** installed ([install guide](https://github.com/astral-sh/uv))
- **Cohere API key** ([sign up for free](https://dashboard.cohere.com/))
- **Qdrant Cloud account** ([sign up for free](https://qdrant.to/cloud))

---

## Step 1: Get API Credentials

### Cohere API Key

1. Go to [Cohere Dashboard](https://dashboard.cohere.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `co-...`)

### Qdrant Cloud Setup

1. Go to [Qdrant Cloud](https://qdrant.to/cloud)
2. Sign up for free tier (no credit card required)
3. Create a new cluster:
   - Name: `my-rag-cluster`
   - Region: Choose closest to you
   - Plan: **Free Tier** (1GB storage)
4. Wait for cluster to provision (~2 minutes)
5. Copy **Cluster URL** (format: `https://xyz.qdrant.io:6333`)
6. Go to **API Keys** → **Create Key** → Copy the key

---

## Step 2: Project Setup

### Clone or Initialize Project

```bash
# Create project directory
mkdir web-embedding-ingestion
cd web-embedding-ingestion

# Initialize UV project
uv init
```

### Install Dependencies

```bash
# Install all required packages
uv pip install \
  beautifulsoup4 \
  aiohttp \
  cohere \
  qdrant-client \
  langchain \
  tiktoken \
  tenacity \
  pydantic \
  python-dotenv \
  tqdm

# Freeze dependencies
uv pip freeze > requirements.txt
```

---

## Step 3: Configure Environment

### Create `.env` File

```bash
# Create .env file with your credentials
cat > .env << 'EOF'
COHERE_API_KEY=your-cohere-api-key-here
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here

# Optional: Override defaults
CHUNK_SIZE=512
CHUNK_OVERLAP=50
EMBEDDING_MODEL=embed-english-v3.0
EMBEDDING_DIM=1024
BATCH_SIZE=5
MAX_RETRIES=3
COLLECTION_NAME=web_documents
EOF
```

**Important**: Replace `your-*-here` with actual values from Step 1.

### Verify Configuration

```bash
# Test environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('Cohere Key:', os.getenv('COHERE_API_KEY')[:10] + '...')"
```

**Expected Output**: `Cohere Key: co-1234567...`

---

## Step 4: Create `main.py`

Download or create the ingestion pipeline:

```bash
# Create backend directory
mkdir backend
cd backend

# Create main.py (content provided separately)
# For now, create placeholder
touch main.py
```

**Note**: The `main.py` implementation will be created during the `/sp.implement` phase. For this quickstart, assume it exists.

---

## Step 5: Run Your First Ingestion

### Simple Test (Single URL)

```python
# test_ingestion.py
import asyncio
from backend.main import main

async def test_single_url():
    result = await main(
        urls=["https://docs.python.org/3/tutorial/introduction.html"],
        verbose=True
    )

    print(f"\n=== Results ===")
    print(f"Success: {result.success_count}")
    print(f"Chunks created: {result.total_chunks}")
    print(f"Time: {result.execution_time_seconds:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_single_url())
```

Run it:
```bash
python test_ingestion.py
```

**Expected Output**:
```
Processing 1 URLs...
Fetching: https://docs.python.org/3/tutorial/introduction.html
Extracting text... (2,345 chars)
Chunking... (5 chunks created)
Generating embeddings... (batch 1/1)
Storing in Qdrant... (5 points uploaded)
[████████████████████████████████] 1/1 URLs processed

=== Results ===
Success: 1
Chunks created: 5
Time: 3.42s
```

---

## Step 6: Verify in Qdrant

### Check Collection Exists

```python
# verify_qdrant.py
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Get collection info
info = client.get_collection("web_documents")
print(f"Collection: {info.name}")
print(f"Points count: {info.points_count}")
print(f"Vector size: {info.config.params.vectors.size}")
```

Run it:
```bash
python verify_qdrant.py
```

**Expected Output**:
```
Collection: web_documents
Points count: 5
Vector size: 1024
```

### Query Stored Content

```python
# query_test.py
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import cohere

load_dotenv()

# Initialize clients
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))

# Generate query embedding
query = "What is Python?"
query_embedding = cohere_client.embed(
    texts=[query],
    model="embed-english-v3.0",
    input_type="search_query"
).embeddings[0]

# Search Qdrant
results = qdrant.search(
    collection_name="web_documents",
    query_vector=query_embedding,
    limit=3
)

print(f"Query: {query}\n")
for i, result in enumerate(results, 1):
    print(f"{i}. Score: {result.score:.4f}")
    print(f"   URL: {result.payload['url']}")
    print(f"   Text: {result.payload['chunk_text'][:100]}...\n")
```

Run it:
```bash
python query_test.py
```

**Expected Output**:
```
Query: What is Python?

1. Score: 0.8524
   URL: https://docs.python.org/3/tutorial/introduction.html
   Text: Python is an easy to learn, powerful programming language. It has efficient high-level data...

2. Score: 0.7912
   URL: https://docs.python.org/3/tutorial/introduction.html
   Text: The Python interpreter is easily extended with new functions and data types implemented in C...

3. Score: 0.7456
   URL: https://docs.python.org/3/tutorial/introduction.html
   Text: Python enables programs to be written compactly and readably. Programs written in Python...
```

---

## Step 7: Batch Ingestion

### Ingest Multiple URLs

```python
# batch_ingestion.py
import asyncio
from backend.main import main

async def ingest_docs():
    urls = [
        "https://docs.python.org/3/tutorial/introduction.html",
        "https://docs.python.org/3/tutorial/controlflow.html",
        "https://docs.python.org/3/tutorial/datastructures.html",
        "https://docs.python.org/3/tutorial/modules.html",
        "https://docs.python.org/3/tutorial/errors.html",
    ]

    result = await main(
        urls=urls,
        batch_size=3,  # Process 3 URLs concurrently
        skip_duplicates=True,  # Skip already ingested URLs
        verbose=True
    )

    print(f"\n=== Batch Ingestion Report ===")
    print(f"Total URLs: {len(urls)}")
    print(f"Success: {result.success_count}")
    print(f"Failed: {result.failed_count}")
    print(f"Skipped: {result.skipped_count}")
    print(f"Total chunks: {result.total_chunks}")
    print(f"Success rate: {result.success_rate:.1f}%")
    print(f"Execution time: {result.execution_time_seconds:.2f}s")

if __name__ == "__main__":
    asyncio.run(ingest_docs())
```

Run it:
```bash
python batch_ingestion.py
```

**Expected Output**:
```
Processing 5 URLs...
[████████████████████████████████] 5/5 URLs processed

=== Batch Ingestion Report ===
Total URLs: 5
Success: 4
Failed: 0
Skipped: 1  (already ingested)
Total chunks: 23
Success rate: 100.0%
Execution time: 12.34s
```

---

## Troubleshooting

### Error: "Invalid Cohere API key"

**Cause**: API key is incorrect or expired

**Solution**:
1. Verify key in [Cohere Dashboard](https://dashboard.cohere.com/)
2. Copy key again (ensure no extra spaces)
3. Update `.env` file: `COHERE_API_KEY=co-...`

---

### Error: "Cannot connect to Qdrant"

**Cause**: Qdrant URL or API key incorrect, or cluster not running

**Solution**:
1. Check cluster status in [Qdrant Cloud Console](https://cloud.qdrant.io/)
2. Verify URL format: `https://xyz.qdrant.io:6333` (include `https://` and `:6333`)
3. Regenerate API key if needed
4. Test connection:
   ```bash
   curl -H "api-key: YOUR_KEY" https://your-cluster.qdrant.io:6333/collections
   ```

---

### Error: "Rate limit exceeded"

**Cause**: Cohere free tier rate limit hit (10 requests/min)

**Solution**:
1. Reduce `batch_size` to 1-2 (slower but avoids rate limits)
2. Upgrade to Cohere paid plan for higher limits
3. Add delays between batches:
   ```python
   result = await main(urls=batch1, batch_size=2)
   await asyncio.sleep(60)  # Wait 1 minute
   result = await main(urls=batch2, batch_size=2)
   ```

---

### Warning: "Text too short, skipping URL"

**Cause**: Extracted text < 50 characters (likely navigation-only page)

**Solution**:
- This is expected behavior (not an error)
- Check URL manually to confirm it's not content-heavy
- If it's a valid page, lower threshold in code (edit validation in `main.py`)

---

## Next Steps

### 1. Integrate with FastAPI

```python
# api.py
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from backend.main import main

app = FastAPI()

class IngestRequest(BaseModel):
    urls: list[HttpUrl]

@app.post("/api/ingest")
async def ingest_urls(request: IngestRequest):
    result = await main(
        urls=[str(url) for url in request.urls],
        verbose=False
    )
    return {
        "success_count": result.success_count,
        "total_chunks": result.total_chunks
    }

# Run with: uvicorn api:app --reload
```

### 2. Automate Ingestion

Create a script to ingest from a URL list:

```bash
# urls.txt
https://docs.python.org/3/tutorial/introduction.html
https://docs.python.org/3/tutorial/controlflow.html
https://docs.python.org/3/tutorial/datastructures.html
```

```python
# ingest_from_file.py
import asyncio
from backend.main import main

async def ingest_from_file(filepath):
    with open(filepath) as f:
        urls = [line.strip() for line in f if line.strip()]

    result = await main(urls=urls, verbose=True)
    print(f"Processed {result.success_count} URLs")

asyncio.run(ingest_from_file("urls.txt"))
```

### 3. Monitor Ingestion

Add logging for production:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion.log'),
        logging.StreamHandler()
    ]
)

result = await main(urls=urls, verbose=True)
logging.info(f"Ingestion complete: {result.success_count} URLs")
```

---

## Resources

- **Cohere Documentation**: https://docs.cohere.com/
- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **LangChain Text Splitters**: https://python.langchain.com/docs/modules/data_connection/document_transformers/
- **UV Package Manager**: https://github.com/astral-sh/uv

---

## Getting Help

- **Issue Tracker**: [GitHub Issues](https://github.com/your-repo/issues)
- **Cohere Community**: https://discord.gg/cohere
- **Qdrant Community**: https://discord.gg/qdrant

---

## Estimated Costs

### Free Tier Limits

- **Cohere**: 100 API calls/month (free trial), 10 requests/min
- **Qdrant Cloud**: 1GB storage (free tier), unlimited queries

### Cost Estimates (Paid Tiers)

| Activity | Volume | Cohere Cost | Qdrant Cost | Total |
|----------|--------|-------------|-------------|-------|
| Ingest 100 URLs | ~1,000 chunks | $0.10 | $0 (free tier) | $0.10 |
| Ingest 1,000 URLs | ~10,000 chunks | $1.00 | $5/month | $6.00 |
| Ingest 10,000 URLs | ~100,000 chunks | $10.00 | $25/month | $35.00 |

**Note**: Costs are approximate and vary based on chunk sizes and embedding dimensions.
