"""Structured operational logs without source text, prompts, identities or keys."""
import json
import logging
import os
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record):
        event = {"timestamp": datetime.now(timezone.utc).isoformat(), "level": record.levelname, "event": record.msg}
        for key in ("strategy", "status", "latency_ms", "evidence_count", "error_type"):
            if hasattr(record, key): event[key] = getattr(record, key)
        return json.dumps(event)


def configure_logging():
    logger = logging.getLogger("qei.pipeline")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.propagate = False
    levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR}
    logger.setLevel(levels.get(os.getenv("QEI_LOG_LEVEL", "INFO").upper(), logging.INFO))
