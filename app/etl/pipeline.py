"""Modular ETL pipeline orchestrator."""

from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional, Union
import uuid
import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.etl.extractors import get_extractor
from app.etl.loaders import get_loader
from app.etl.transformers import get_transformer
from app.etl.validators import get_validator
from app.models.common import IngestionBatch
from app.utils.logger import logger


class ETLPipeline:
    """Orchestrates Extract -> Validate -> Transform -> Load -> Logs -> Analytics."""

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def run(
        self,
        source: Any,
        domain: str = "retail",
        source_type: str = "csv",
        source_name: Optional[str] = None,
        db: Optional[Session] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute the complete end-to-end data pipeline."""
        start_time = time.time()
        batch_id = str(uuid.uuid4())
        session = db or self._db or SessionLocal()
        should_close_session = (db is None and self._db is None)

        if not source_name:
            source_name = str(source) if isinstance(source, (str, int)) else f"upload_{source_type}_{batch_id[:8]}"

        # 1. Initialize Batch Metadata in DB
        batch_record = IngestionBatch(
            batch_id=batch_id,
            domain=domain.lower(),
            source_type=source_type.lower(),
            source_name=str(source_name),
            status="running",
            total_records=0,
            valid_records=0,
            rejected_records=0,
            started_at=datetime.now(timezone.utc),
        )
        session.add(batch_record)
        session.commit()

        # 2. Structured Log - Pipeline Start
        logger.log_pipeline_start(batch_id=batch_id, domain=domain, source=str(source_name))

        try:
            # 3. EXTRACT
            extractor = get_extractor(source_type)
            raw_df = extractor.extract(source, **kwargs)
            total_records = len(raw_df)
            batch_record.total_records = total_records
            session.commit()

            # 4. VALIDATE
            validator = get_validator(domain)
            val_result = validator.validate(raw_df)

            # Log validation failures
            for item in val_result.rejected_items:
                logger.log_validation_error(batch_id, item.record_index, item.reasons)

            # 5. TRANSFORM
            transformer = get_transformer(domain)
            transformed_df = transformer.transform(val_result.valid_df)

            # 6. LOAD
            loader = get_loader(domain)
            load_summary = loader.load(
                df=transformed_df,
                batch_id=batch_id,
                rejected_items=val_result.rejected_items,
                db=session,
                source_name=str(source_name),
            )

            # 7. LOGS & METRICS UPDATE
            duration = round(time.time() - start_time, 3)
            batch_record.status = "completed"
            batch_record.valid_records = val_result.valid_count
            batch_record.rejected_records = val_result.rejected_count
            batch_record.completed_at = datetime.now(timezone.utc)
            batch_record.execution_time_sec = duration
            batch_record.set_metadata({
                "rule_violations": val_result.rule_counts,
                "entities_loaded": load_summary.get("entities_affected", {}),
                "total_inserted": load_summary.get("inserted_records", 0),
            })
            session.commit()

            logger.log_pipeline_complete(
                batch_id=batch_id,
                duration_sec=duration,
                valid=val_result.valid_count,
                rejected=val_result.rejected_count,
            )

            # 8. GENERATE ANALYTICS SUMMARY
            return {
                "batch_id": batch_id,
                "domain": domain,
                "source_name": source_name,
                "status": "completed",
                "total_records": total_records,
                "valid_records": val_result.valid_count,
                "rejected_records": val_result.rejected_count,
                "data_quality_pct": round((val_result.valid_count / total_records * 100), 2) if total_records > 0 else 100.0,
                "rule_violations": val_result.rule_counts,
                "entities_affected": load_summary.get("entities_affected", {}),
                "execution_time_sec": duration,
            }

        except Exception as exc:
            duration = round(time.time() - start_time, 3)
            logger.exception(f"Pipeline failed for batch {batch_id}", error=str(exc))
            try:
                batch_record.status = "failed"
                batch_record.completed_at = datetime.now(timezone.utc)
                batch_record.execution_time_sec = duration
                batch_record.set_metadata({"error": str(exc)})
                session.commit()
            except Exception:
                session.rollback()

            return {
                "batch_id": batch_id,
                "domain": domain,
                "source_name": source_name,
                "status": "failed",
                "error": str(exc),
                "execution_time_sec": duration,
            }
        finally:
            if should_close_session:
                session.close()
