# Quickstart Guide: RAG Chatbot Backend

**Feature**: 001-rag-chatbot-backend
**Date**: 2025-12-24
**Audience**: Developers setting up the backend for local development or deployment

## Overview

This guide walks you through setting up the RAG Chatbot Backend from scratch, including all dependencies, configuration, and testing. Estimated setup time: 15-20 minutes.

---

## Prerequisites

### Required
- Python 3.10 or higher
- Git
- Text editor or IDE
- OpenAI API key (for embeddings and LLM)
- Qdrant Cloud account (free tier)
- Neon Serverless Postgres account (free tier)

### Optional
- Docker (for containerized development)
- Postman or curl (for API testing)

---

## Step 1: Clone Repository

```bash
git clone https://github.com/your-username/book_hackathon.git
cd book_hackathon
git checkout 001-rag-chatbot-backend
```

---

## Step 2: Set Up Python Environment

### Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install requirements
pip install -r requirements.txt
```

**Expected `requirements.txt` contents**:
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
openai==1.54.0
qdrant-client==1.11.0
psycopg2-binary==2.9.9
sqlalchemy[asyncio]==2.0.35
pydantic==2.9.0
pydantic-settings==2.5.0
python-dotenv==1.0.1
langchain-text-splitters==0.3.0
slowapi==0.1.9
httpx==0.27.0
```

---

## Step 3: Configure External Services

### 3.1 OpenAI API Setup

1. Visit [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)
4. Add billing information (required for API access)
5. Verify quota: At least $5 credit recommended for development

### 3.2 Qdrant Cloud Setup

1. Visit [https://cloud.qdrant.io](https://cloud.qdrant.io)
2. Sign up for free account
3. Create a new cluster:
   - Name: `textbook-chatbot`
   - Region: Choose closest to your location
   - Plan: Free tier (1GB storage, 100K vectors)
4. Note the cluster URL (e.g., `https://abc123.qdrant.io`)
5. Create API key in cluster settings
6. Copy the API key

### 3.3 Neon Postgres Setup

1. Visit [https://neon.tech](https://neon.tech)
2. Sign up for free account
3. Create a new project:
   - Name: `rag-chatbot`
   - Region: Choose closest to your location
   - Plan: Free tier (512MB storage, 3GB transfer)
4. Copy the connection string (format: `postgresql://user:pass@host/dbname`)
5. Note: Connection string includes password

---

## Step 4: Environment Configuration

Create a `.env` file in the `backend/` directory:

```bash
# Copy example file
cp .env.example .env

# Edit .env with your credentials
```

**`.env` file contents**:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Qdrant Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here

# Neon Postgres Configuration
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# CORS Configuration (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Security Note**: Never commit `.env` to version control. It's already in `.gitignore`.

---

## Step 5: Database Initialization

Run database migrations to create tables:

```bash
# From backend/ directory
python scripts/init_database.py
```

**Expected output**:
```
Connecting to Neon Postgres...
Creating tables...
✓ Created users table
✓ Created sessions table
✓ Created messages table
✓ Created document_chunks table
✓ Created health_status table
✓ Created indexes
✓ Created triggers
Database initialization complete!
```

---

## Step 6: Initialize Qdrant Collection

Create the vector collection for textbook chunks:

```bash
python scripts/init_qdrant.py
```

**Expected output**:
```
Connecting to Qdrant Cloud...
Creating collection 'textbook_chunks'...
✓ Collection created with 1536 dimensions (COSINE distance)
✓ HNSW index configured (m=16, ef_construct=100)
Qdrant initialization complete!
```

---

## Step 7: Ingest Textbook Content

Process and index textbook markdown files:

```bash
# Assuming textbook markdown is in ../docs directory
python scripts/ingest_book.py --source-dir ../docs --chunk-size 512 --overlap 51
```

**Expected output**:
```
Loading markdown files from ../docs...
Found 25 markdown files

Processing files...
[====================] 25/25 files processed

Chunking content...
Created 487 chunks (avg 512 tokens)

Generating embeddings...
[====================] 487/487 chunks embedded (batch size: 100)

Storing in Qdrant...
✓ All chunks indexed

Storing metadata in Postgres...
✓ Metadata saved

Ingestion Summary:
- Total files: 25
- Total chunks: 487
- Total tokens: ~249,344
- Ingestion time: 45.3 seconds
- OpenAI API cost: ~$0.50

✓ Ingestion complete!
```

**Troubleshooting**:
- If OpenAI rate limit error: Reduce batch size with `--batch-size 50`
- If Qdrant timeout: Check network connection and cluster status
- If markdown parsing error: Verify files use standard markdown syntax

---

## Step 8: Start Development Server

Run the FastAPI server locally:

```bash
# From backend/ directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access Points**:
- API Base: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

---

## Step 9: Test the API

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-24T10:30:00Z",
  "dependencies": {
    "qdrant": "connected",
    "postgres": "connected",
    "openai": "available"
  },
  "response_time_ms": 45
}
```

### Test 2: Send Chat Message (Full Textbook Mode)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "full_textbook",
    "message": "What is inverse kinematics?"
  }'
```

**Expected response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "660e8400-e29b-41d4-a716-446655440000",
  "response": "Inverse kinematics is the process of determining the joint angles needed to place a robot's end effector at a desired position and orientation...",
  "retrieved_chunks": 5,
  "timestamp": "2025-12-24T10:30:15Z"
}
```

### Test 3: Selection-Only Mode

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "selection_only",
    "message": "Explain this code",
    "selected_text": "def forward_kinematics(angles):\\n    return calculate_position(angles)"
  }'
```

**Expected response**:
```json
{
  "session_id": "770e8400-e29b-41d4-a716-446655440000",
  "message_id": "880e8400-e29b-41d4-a716-446655440000",
  "response": "This code defines a function called forward_kinematics that takes joint angles as input and returns the calculated position of the robot's end effector...",
  "retrieved_chunks": 0,
  "timestamp": "2025-12-24T10:30:20Z"
}
```

### Test 4: Retrieve Session History

```bash
curl http://localhost:8000/api/sessions/550e8400-e29b-41d4-a716-446655440000
```

---

## Step 10: Frontend Integration

### CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:3000` (local development)
- Your Vercel deployment URL (production)

Update `ALLOWED_ORIGINS` in `.env` to match your frontend URL.

### Frontend Usage Example

```javascript
// In your Vercel-hosted frontend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function sendChatMessage(message, sessionId = null) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      mode: 'full_textbook',
      message: message,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return await response.json();
}

// Usage
const result = await sendChatMessage('What is inverse kinematics?');
console.log(result.response);
```

---

## Deployment (Render)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "feat: complete RAG chatbot backend"
git push origin 001-rag-chatbot-backend
```

### Step 2: Create Render Service

1. Visit [https://render.com](https://render.com)
2. Sign up and connect GitHub account
3. Click "New +" → "Web Service"
4. Select your repository and branch
5. Configure:
   - Name: `rag-chatbot-api`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Instance Type: Free or Starter ($7/month)

### Step 3: Add Environment Variables

In Render dashboard, add all variables from your `.env`:
- `OPENAI_API_KEY`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `DATABASE_URL`
- `ALLOWED_ORIGINS` (include your Vercel URL)
- `ENVIRONMENT=production`

### Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Wait for deployment to complete (~5 minutes)
4. Note your service URL (e.g., `https://rag-chatbot-api.onrender.com`)

### Step 5: Run Post-Deploy Scripts

```bash
# Initialize database (one-time)
curl -X POST https://rag-chatbot-api.onrender.com/admin/init-db

# Ingest content (one-time or on content updates)
curl -X POST https://rag-chatbot-api.onrender.com/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"source_dir": "/app/docs"}'
```

### Step 6: Update Frontend

Update your Vercel frontend environment variables:
```bash
NEXT_PUBLIC_API_URL=https://rag-chatbot-api.onrender.com
```

Redeploy frontend for changes to take effect.

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure you activated the virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: OpenAI rate limit errors

**Solution**: Reduce request frequency or upgrade OpenAI plan. For development, add delays between requests:
```python
import asyncio
await asyncio.sleep(1)  # 1 second delay between API calls
```

### Issue: Qdrant connection timeout

**Solution**:
1. Verify cluster is running in Qdrant Cloud dashboard
2. Check API key is correct
3. Ensure firewall allows outbound HTTPS connections
4. Try pinging cluster: `curl https://your-cluster.qdrant.io`

### Issue: Database connection failed

**Solution**:
1. Verify Neon project is active
2. Check connection string includes `?sslmode=require`
3. Ensure password doesn't contain special characters that need URL encoding
4. Test connection: `psql "postgresql://user:pass@host/db?sslmode=require"`

### Issue: CORS errors from frontend

**Solution**:
1. Verify `ALLOWED_ORIGINS` in `.env` includes your frontend URL
2. Restart backend server after changing `.env`
3. Check browser console for exact CORS error
4. Ensure frontend is using correct API URL

---

## Next Steps

✅ **Backend is running!**

Now you can:
1. Test all API endpoints using `/docs` (Swagger UI)
2. Integrate with your Vercel frontend
3. Monitor health endpoint for uptime
4. Add more textbook content via ingestion endpoint
5. Review logs for debugging: `tail -f logs/app.log`

For implementation tasks and development workflow, see `tasks.md` (generated by `/sp.tasks`).

---

## Useful Commands

```bash
# Start server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Check code style
black app/ --check
flake8 app/

# View logs
tail -f logs/app.log

# Database migrations
alembic upgrade head

# Cleanup old sessions
python scripts/cleanup_sessions.py --days 7
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Neon Postgres Docs](https://neon.tech/docs/introduction)
- [Render Deployment Guide](https://render.com/docs/deploy-fastapi)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review API documentation at `/docs`
3. Check logs for error details
4. Open GitHub issue with error logs and steps to reproduce
