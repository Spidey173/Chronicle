"""Audit service for logging system actions and entity changes."""

import json
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.models.user import AuditLog
from app.utils.logger import logger


class AuditService:
    """Manages compliance audit trails."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_id: Optional[int] = None,
        details: Optional[Any] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        details_str = json.dumps(details, default=str) if isinstance(details, (dict, list)) else (str(details) if details else None)
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details_str,
            ip_address=ip_address,
        )
        try:
            db.add(entry)
            db.commit()
            return entry
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to record audit log: {exc}")
            raise
