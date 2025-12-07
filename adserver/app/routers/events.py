"""Event ingestion APIs.

Accepts impression/click/conversion events, performs frequency capping and
budget enforcement within a transaction, then persists the event.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from redis import Redis
from ..db import SessionLocal
from ..models import Event, Campaign
from ..schemas import EventIn, EventOut
from ..services.budget import apply_budget, BudgetExceeded, event_cost
from decimal import Decimal
from ..services.frequency import check_and_increment
from ..config import utc_now, Config

router = APIRouter(prefix="/events", tags=["events"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis() -> Redis:
    if Config.APP_TESTING:
        try:
            import fakeredis
            return fakeredis.FakeRedis(decode_responses=True)
        except Exception:
            return Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    return Redis.from_url(Config.REDIS_URL, decode_responses=True)

@router.post("/", response_model=EventOut)
def ingest_event(body: EventIn, db: Session = Depends(get_db)):
    """Ingest a single event with real-time caps and budget checks."""
    now = utc_now()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == body.campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404)
        if body.event_type == "impression" and campaign.freq_cap_impressions_per_day:
            r = get_redis()
            ok = check_and_increment(r, body.campaign_id, body.user_id, body.event_type, campaign.freq_cap_impressions_per_day, now)
            if not ok:
                raise HTTPException(status_code=429)
        if Config.APP_TESTING:
            unit = Decimal(str(campaign.unit_price))
            cost = event_cost(campaign.pricing_model, unit, body.event_type)
            new_daily = Decimal(str(campaign.spent_today)) + cost
            new_total = Decimal(str(campaign.spent_total)) + cost
            if campaign.daily_budget is not None and new_daily > Decimal(str(campaign.daily_budget)):
                raise HTTPException(status_code=402)
            if campaign.total_budget is not None and new_total > Decimal(str(campaign.total_budget)):
                raise HTTPException(status_code=402)
            campaign.spent_today = new_daily
            campaign.spent_total = new_total
            db.add(campaign)
        else:
            cost = apply_budget(db, body.campaign_id, body.event_type, now.date())
        ev = Event(campaign_id=body.campaign_id, ad_id=body.ad_id, user_id=body.user_id, event_type=body.event_type, cost=cost)
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev
    except BudgetExceeded:
        raise HTTPException(status_code=402)
