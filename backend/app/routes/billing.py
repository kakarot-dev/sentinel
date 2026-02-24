from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.billing import BillingRecord
from app.schemas.billing import (
    BillingBatchCreate,
    BillingCreate,
    BillingResponse,
    SeedResponse,
    BillingSummary
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

@router.get('/', response_model=list[BillingResponse])
def get_billing(
        service: str = Query(default=None),
        region: str = Query(default=None),
        db: Session = Depends(get_db)
):
    stmt = db.query(BillingRecord)
    if service:
        stmt = stmt.filter_by(service=service)
    if region:
        stmt = stmt.filter_by(region=region)
    records = stmt.all()
    return records

@router.get('/summary', response_model=list[BillingSummary])
def get_summary(
        db: Session = Depends(get_db)
):
    total_cost = db.query(BillingRecord.service, func.sum(BillingRecord.cost).label("total_cost")).group_by(BillingRecord.service)
    billing_data = [BillingSummary(service=row.service, total_cost=row.total_cost) for row in total_cost]
    return billing_data

@router.get('/{id}', response_model=BillingResponse)
def get_info(
        id: int,
        db: Session = Depends(get_db)
):
    record = db.get(BillingRecord, id)
    if not record:
        raise HTTPException(detail="Billing Record not found", status_code=404)
    return record
