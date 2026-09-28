"""Data Ingestion endpoints: file uploads, batch status, dead-letter queue."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.etl.pipeline import ETLPipeline
from app.models.common import IngestionBatch, RejectedRecord
from app.models.user import User
from app.schemas.common import (
    IngestionBatchResponse,
    PaginatedResponse,
    PaginationMeta,
    RejectedRecordResponse,
)
from app.services.audit_service import AuditService
from app.services.storage_service import storage_service
from app.utils.pagination import paginate_query

router = APIRouter(prefix="", tags=["Data Ingestion"])


@router.post("/upload", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile = File(..., description="File to ingest (CSV, Excel .xlsx, JSON)"),
    domain: str = Form("retail", description="Target domain: 'retail' or 'banking'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a data file (CSV, Excel, JSON) and trigger the automated ETL pipeline."""
    filename = file.filename or "unknown_file"
    ext = Path(filename).suffix.lower()

    # Determine source type
    if ext in [".csv"]:
        source_type = "csv"
    elif ext in [".xlsx", ".xls"]:
        source_type = "excel"
    elif ext in [".json"]:
        source_type = "json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: CSV (.csv), Excel (.xlsx, .xls), JSON (.json)",
        )

    # Save uploaded file
    try:
        saved_path = storage_service.save_upload_file(file)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to store file: {exc}")

    # Save user_id before pipeline transaction
    user_id = current_user.id

    # Execute ETL Pipeline
    pipeline = ETLPipeline(db=db)
    result = pipeline.run(
        source=str(saved_path),
        domain=domain,
        source_type=source_type,
        source_name=filename,
        db=db,
    )

    AuditService.log_action(
        db,
        action="DATA_INGESTION_UPLOAD",
        entity_type="ingestion_batch",
        entity_id=result.get("batch_id"),
        user_id=user_id,
        details={"filename": filename, "domain": domain, "status": result.get("status")},
    )

    return result


@router.post("/ingestion/trigger-api", response_model=Dict[str, Any])
def trigger_rest_api_ingestion(
    api_url: str = Query(..., description="REST endpoint URL to pull data from"),
    domain: str = Query("retail", description="Target domain"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    """Trigger ingestion by pulling records from an external REST API (Admin only)."""
    pipeline = ETLPipeline(db=db)
    result = pipeline.run(
        source=api_url,
        domain=domain,
        source_type="rest_api",
        source_name=api_url,
        db=db,
    )
    return result


@router.get("/ingestion/batches", response_model=PaginatedResponse[IngestionBatchResponse])
def list_batches(
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by batch status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve historical ingestion batches and their operational metrics."""
    query = db.query(IngestionBatch)
    if domain:
        query = query.filter(IngestionBatch.domain == domain.lower())
    if status_filter:
        query = query.filter(IngestionBatch.status == status_filter.lower())
    query = query.order_by(IngestionBatch.started_at.desc())

    # Form response items with metadata
    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
    batches = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for b in batches:
        b_dict = {
            "id": b.id,
            "batch_id": b.batch_id,
            "domain": b.domain,
            "source_type": b.source_type,
            "source_name": b.source_name,
            "status": b.status,
            "total_records": b.total_records,
            "valid_records": b.valid_records,
            "rejected_records": b.rejected_records,
            "started_at": b.started_at,
            "completed_at": b.completed_at,
            "execution_time_sec": b.execution_time_sec,
            "metadata": b.get_metadata(),
        }
        items.append(IngestionBatchResponse(**b_dict))

    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return PaginatedResponse(items=items, pagination=pagination)


@router.get("/ingestion/quarantine", response_model=PaginatedResponse[RejectedRecordResponse])
def get_quarantined_records(
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Inspect dead-letter queue records and reasons for validation rejections."""
    query = db.query(RejectedRecord)
    if batch_id:
        query = query.filter(RejectedRecord.batch_id == batch_id)
    if domain:
        query = query.filter(RejectedRecord.domain == domain.lower())
    query = query.order_by(RejectedRecord.created_at.desc())

    total_records = query.count()
    total_pages = (total_records + page_size - 1) // page_size if total_records > 0 else 1
    records = query.offset((page - 1) * page_size).limit(page_size).all()

    items = [
        RejectedRecordResponse(
            id=r.id,
            batch_id=r.batch_id,
            domain=r.domain,
            source_identifier=r.source_identifier,
            record_index=r.record_index,
            raw_data=r.get_raw_data(),
            rejection_reasons=r.get_reasons(),
            created_at=r.created_at,
        )
        for r in records
    ]

    pagination = PaginationMeta(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
    return PaginatedResponse(items=items, pagination=pagination)
