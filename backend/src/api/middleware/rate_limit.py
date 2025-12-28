from slowapi import Limiter, get_remote_address
from slowapi.util import get_ipaddr
from slowapi.errors import RateLimitExceeded
from fastapi import HTTPException, Request
from typing import Callable

limiter = Limiter(key_func=get_remote_address)
slow = Limiter(key_func=get_ipaddr, default_limits=["10/minute"])

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    raise HTTPException(
        status_code=429,
        detail=f"Rate limit exceeded. Please wait {exc.retry_after} seconds.",
        headers={"Retry-After": str(exc.retry_after)},
    )
