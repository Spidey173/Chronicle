"""Ingestion batch and quarantine (rejected records) models."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class IngestionBatch(Base):
    """Tracks batch execution lifecycle, metadata, and quality metrics."""

    __tablename__ = "ingestion_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), unique=True, index=True, nullable=False)
    domain = Column(String(50), nullable=False, index=True)  # "retail", "banking", etc.
    source_type = Column(String(50), nullable=False)        # "csv", "json", "excel", "rest_api"
    source_name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, running, completed, failed
    total_records = Column(Integer, default=0, nullable=False)
    valid_records = Column(Integer, default=0, nullable=False)
    rejected_records = Column(Integer, default=0, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    execution_time_sec = Column(Float, default=0.0, nullable=False)
    metadata_json = Column(Text, nullable=True)

    rejections = relationship("RejectedRecord", back_populates="batch", cascade="all, delete-orphan")

    def set_metadata(self, data: Dict[str, Any]) -> None:
        self.metadata_json = json.dumps(data)

    def get_metadata(self) -> Dict[str, Any]:
        return json.loads(self.metadata_json) if self.metadata_json else {}


class RejectedRecord(Base):
    """Dead letter queue / quarantine table for rejected records with failure reasons."""

    __tablename__ = "rejected_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(64), ForeignKey("ingestion_batches.batch_id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String(50), nullable=False, index=True)
    source_identifier = Column(String(255), nullable=False)
    record_index = Column(Integer, nullable=False)
    raw_data_json = Column(Text, nullable=False)
    rejection_reasons_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    batch = relationship("IngestionBatch", back_populates="rejections")

    def set_raw_data(self, data: Any) -> None:
        self.raw_data_json = json.dumps(data, default=str)

    def get_raw_data(self) -> Any:
        return json.loads(self.raw_data_json) if self.raw_data_json else {}

    def set_reasons(self, reasons: List[str]) -> None:
        self.rejection_reasons_json = json.dumps(reasons)

    def get_reasons(self) -> List[str]:
        return json.loads(self.rejection_reasons_json) if self.rejection_reasons_json else []
