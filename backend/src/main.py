from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .models.database import settings, init_db
from .api.routes import health, auth
from .api.middleware.security import SecurityHeadersMiddleware
from .api.middleware.auth import AuthMiddleware
from .api.middleware.logging import structured_logger
from .api.middleware.rate_limit import limiter, slow

app = FastAPI(title="Authenticated RAG Backend")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware, app)

# Authentication Middleware
app.add_middleware(AuthMiddleware, app)

# Configure slowapi
app.state.limiter = limiter

# Include routes
# Note: Auth routes must be included BEFORE AuthMiddleware to allow authentication
app.include_router(auth.router)
app.include_router(health.router, tags=["Health"])

# Health check endpoint
@app.get("/health")
@slow
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    structured_logger.log_error("info", "Application started", message="Backend service initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
