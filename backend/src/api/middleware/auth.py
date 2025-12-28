from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ...services.auth import verify_session
from ...models.database import get_db

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Skip auth for auth endpoints (not in MVP but future-proof)
        if "/api/auth/" in request.url.path:
            return await call_next(request)

        # Extract session token from cookie
        session_token = request.cookies.get("session_token")

        if not session_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )

        # Verify session
        db = next(get_db())
        user = verify_session(db, session_token)

        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired session"}
            )

        # Add user to request state
        request.state.user = user

        return await call_next(request)
