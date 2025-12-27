import logging
import json
from datetime import datetime
from fastapi import Request
from typing import Callable

logger = logging.getLogger(__name__)

class StructuredLogger:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s'
        )

    def log_auth_event(self, event_type: str, user_id: str, **kwargs):
        log_entry = {
            "event": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.info(json.dumps(log_entry))

    def log_error(self, error_type: str, error_message: str, **kwargs):
        log_entry = {
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        logger.error(json.dumps(log_entry))

structured_logger = StructuredLogger()
