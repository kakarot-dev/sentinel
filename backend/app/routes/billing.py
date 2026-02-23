from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.billing import BillingRecord
from app.schemas.billing import (
    BillingBatchCreate,
    BillingCreate,
    BillingResponse,
    SeedResponse,
)
from app.services.mock_data import generate_mock_records

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])


@router.post("/", response_model=BillingResponse, status_code=201)
def ingest_single(record: BillingCreate, db: Session = Depends(get_db)):
    """Ingest a single billing record."""
    db_record = BillingRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.post("/batch", response_model=list[BillingResponse], status_code=201)
def ingest_batch(batch: BillingBatchCreate, db: Session = Depends(get_db)):
    """Ingest a batch of billing records."""
    db_records = [BillingRecord(**r.model_dump()) for r in batch.records]
    db.add_all(db_records)
    db.commit()
    for r in db_records:
        db.refresh(r)
    return db_records


@router.post("/seed", response_model=SeedResponse, status_code=201)
def seed_mock_data(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Generate and ingest realistic mock AWS billing data."""
    records = generate_mock_records(days=days)
    db.add_all(records)
    db.commit()
    return SeedResponse(
        message=f"Seeded {len(records)} billing records over {days} days",
        records_created=len(records),
    )
