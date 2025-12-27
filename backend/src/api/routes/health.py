from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="", tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
