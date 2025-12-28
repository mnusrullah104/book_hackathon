---
title: AI-Native Robotics RAG Backend
emoji: 🤖
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# AI-Native Robotics RAG Backend

Authenticated RAG (Retrieval-Augmented Generation) backend for the Physical AI & Humanoid Robotics textbook.

## Features

- **Authentication**: User registration, sign-in, sign-out with secure session cookies
- **RAG Chat**: OpenAI/OpenRouter powered chat with vector search retrieval
- **Vector Database**: Qdrant Cloud for semantic document search
- **PostgreSQL**: Neon Serverless for user and session storage

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/auth/register` | POST | User registration |
| `/api/auth/sign-in` | POST | User sign-in |
| `/api/auth/sign-out` | POST | User sign-out |
| `/api/chat/message` | POST | RAG-powered chat |
| `/api/chat/status` | GET | Chat service status |

## Environment Variables

Required secrets (set in HuggingFace Space settings):

- `DATABASE_URL` - Neon PostgreSQL connection string
- `SECRET_KEY` - Session signing key
- `FRONTEND_URL` - Vercel frontend URL for CORS
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM
- `COHERE_API_KEY` - Cohere API key for embeddings
- `QDRANT_URL` - Qdrant Cloud instance URL
- `QDRANT_API_KEY` - Qdrant API key

## Tech Stack

- FastAPI + Uvicorn
- SQLAlchemy + Neon PostgreSQL
- Qdrant Cloud + Cohere Embeddings
- OpenRouter (Mistral/GPT models)
