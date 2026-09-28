"""Common shared schemas: pagination, batches, dead-letter records, health."""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None
    success: bool = True


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMeta


class IngestionBatchResponse(BaseModel):
    id: int
    batch_id: str
    domain: str
    source_type: str
    source_name: str
    status: str
    total_records: int
    valid_records: int
    rejected_records: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time_sec: float
    metadata: Dict[str, Any] = {}

    model_config = {"from_attributes": True}


class RejectedRecordResponse(BaseModel):
    id: int
    batch_id: str
    domain: str
    source_identifier: str
    record_index: int
    raw_data: Any
    rejection_reasons: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: str
    timestamp: datetime
    version: str
