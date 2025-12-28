# Backend Deployment to HuggingFace Spaces

## Step 1: Create HuggingFace Space

1. Go to https://huggingface.co/new-space
2. Fill in:
   - **Space name**: `robotics-rag-backend`
   - **SDK**: Select **Docker**
   - **Visibility**: Public (or Private if you have Pro)
3. Click **Create Space**

## Step 2: Clone and Setup

```bash
# Clone your new HuggingFace Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/robotics-rag-backend
cd robotics-rag-backend

# Copy backend files from your project
cp -r /path/to/book_hackathon_main/backend/* .

# Make sure these files exist:
# - Dockerfile
# - requirements.txt
# - src/ (folder with FastAPI app)
# - agent.py
# - retrieve.py
# - main.py (ingestion pipeline with exceptions)
```

## Step 3: Set Environment Variables

Go to your Space → Settings → **Repository secrets**

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `DATABASE_URL` | `postgresql://neondb_owner:npg_Ly9UORKo8ert@ep-plain-violet-adu773n5-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require` |
| `SECRET_KEY` | `your-generated-secret-key-here` |
| `FRONTEND_URL` | `https://book-hackathon-blond.vercel.app` |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` |
| `COHERE_API_KEY` | `BRLcAfrYW3nSA...` |
| `QDRANT_URL` | `https://073aee9c-1e3d-4ba4-b0eb-2b94ed925184.us-east4-0.gcp.cloud.qdrant.io` |
| `QDRANT_API_KEY` | `eyJhbGciOi...` |

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 4: Push to HuggingFace

```bash
cd robotics-rag-backend
git add .
git commit -m "Initial deployment"
git push
```

## Step 5: Verify Deployment

1. Go to your Space page
2. Wait for Docker build to complete (3-5 minutes)
3. Check the Logs tab for errors
4. Test the health endpoint:

```bash
curl https://YOUR_USERNAME-robotics-rag-backend.hf.space/health
```

Expected response:
```json
{"status": "healthy", "timestamp": "2024-12-28T..."}
```

## Step 6: Update Frontend

Update `frontend/.env.local`:
```
API_URL=https://YOUR_USERNAME-robotics-rag-backend.hf.space/api
```

Then redeploy frontend to Vercel:
```bash
cd frontend
git add .env.local
git commit -m "Update API_URL to production backend"
git push
```

## Troubleshooting

### Build Fails
- Check Dockerfile syntax
- Verify all requirements are in requirements.txt
- Check Logs tab for specific errors

### API Returns 500
- Verify all environment secrets are set
- Check if DATABASE_URL is correct
- Verify QDRANT connection

### CORS Errors
- Ensure FRONTEND_URL matches exactly (no trailing slash)
- Check browser Network tab for actual error

## Quick Test Commands

```bash
# Test health
curl https://YOUR-SPACE.hf.space/health

# Test chat status
curl https://YOUR-SPACE.hf.space/api/chat/status

# Test registration
curl -X POST https://YOUR-SPACE.hf.space/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

---

**Your HuggingFace Space URL will be:**
`https://YOUR_USERNAME-robotics-rag-backend.hf.space`
