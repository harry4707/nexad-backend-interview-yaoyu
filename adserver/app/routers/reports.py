from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..reports import campaign_report

router = APIRouter(prefix="/report", tags=["report"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/campaign/{campaign_id}")
def report_campaign(campaign_id: int, start: str | None = None, end: str | None = None, db: Session = Depends(get_db)):
    return campaign_report(db, campaign_id, start, end)
