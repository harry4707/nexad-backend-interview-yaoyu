from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Campaign
from ..schemas import CampaignCreate, CampaignOut

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CampaignOut)
def create_campaign(body: CampaignCreate, db: Session = Depends(get_db)):
    c = Campaign(
        name=body.name,
        pricing_model=body.pricing_model,
        unit_price=body.unit_price,
        total_budget=body.total_budget,
        daily_budget=body.daily_budget,
        freq_cap_impressions_per_day=body.freq_cap_impressions_per_day,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

@router.get("/{campaign_id}", response_model=CampaignOut)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404)
    return c
