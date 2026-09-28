"""Integration tests for the complete ETL pipeline."""

import io
from app.etl.pipeline import ETLPipeline
from app.models.common import IngestionBatch, RejectedRecord
from app.models.retail import Customer, Order, OrderItem, Product


def test_pipeline_end_to_end_retail(db_session):
    csv_data = io.StringIO(
        "order_number,customer_email,product_code,order_date,quantity,unit_price,currency\n"
        "ORD-TEST-1,user1@test.com,PRD-1,2026-05-10,2,50.0,USD\n"
        "ORD-TEST-2,user2@test.com,PRD-2,2026-05-11,1,120.0,USD\n"
        "ORD-TEST-ERR,invalid-email,PRD-3,2026-05-12,1,80.0,USD\n"  # Invalid email, should be quarantined
    )

    pipeline = ETLPipeline(db=db_session)
    result = pipeline.run(
        source=csv_data,
        domain="retail",
        source_type="csv",
        source_name="test_retail_feed.csv",
        db=db_session,
    )

    assert result["status"] == "completed"
    assert result["total_records"] == 3
    assert result["valid_records"] == 2
    assert result["rejected_records"] == 1
    assert result["data_quality_pct"] == 66.67

    # Verify Database State
    batch = db_session.query(IngestionBatch).filter(IngestionBatch.batch_id == result["batch_id"]).first()
    assert batch is not None
    assert batch.status == "completed"
    assert batch.valid_records == 2
    assert batch.rejected_records == 1

    # Verify Quarantined Record in RejectedRecord table
    rejected = db_session.query(RejectedRecord).filter(RejectedRecord.batch_id == result["batch_id"]).first()
    assert rejected is not None
    assert any("Invalid email" in r for r in rejected.get_reasons())

    # Verify Orders created in DB
    orders = db_session.query(Order).all()
    assert len(orders) >= 2
