"""Structured logging utility with JSON and colorized console formatting."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Include custom extra fields if provided
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj["data"] = record.extra_data

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class StructuredLogger:
    """Wrapper around standard logger to provide structured event logging."""

    def __init__(self, name: str = "platform"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)
            self.logger.propagate = False

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, **kwargs)

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, **kwargs)

    def exception(self, msg: str, **kwargs: Any) -> None:
        self.logger.exception(msg, extra={"extra_data": kwargs})

    def _log(self, level: int, msg: str, **kwargs: Any) -> None:
        extra_data = kwargs if kwargs else None
        self.logger.log(level, msg, extra={"extra_data": extra_data})

    # Domain specific event helpers
    def log_pipeline_start(self, batch_id: str, domain: str, source: str) -> None:
        self.info("Pipeline execution started", event="pipeline_start", batch_id=batch_id, domain=domain, source=source)

    def log_pipeline_complete(self, batch_id: str, duration_sec: float, valid: int, rejected: int) -> None:
        self.info(
            "Pipeline execution completed",
            event="pipeline_complete",
            batch_id=batch_id,
            duration_sec=duration_sec,
            valid_records=valid,
            rejected_records=rejected,
        )

    def log_validation_error(self, batch_id: str, record_index: int, reasons: list) -> None:
        self.warning(
            "Record validation failed",
            event="validation_error",
            batch_id=batch_id,
            record_index=record_index,
            reasons=reasons,
        )

    def log_database_insert(self, table: str, count: int, batch_id: Optional[str] = None) -> None:
        self.info(
            f"Successfully inserted {count} records into {table}",
            event="db_insert",
            table=table,
            count=count,
            batch_id=batch_id,
        )

    def log_upload_failed(self, filename: str, reason: str) -> None:
        self.error("File upload failed", event="upload_failed", filename=filename, reason=reason)

    def log_api_request(self, method: str, path: str, status_code: int, duration_ms: float, client_ip: str) -> None:
        self.info(
            f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
            event="api_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            client_ip=client_ip,
        )


logger = StructuredLogger("analytics_platform")
