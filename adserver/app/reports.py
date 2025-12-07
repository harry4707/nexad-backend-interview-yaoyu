"""Reporting utilities.

Aggregates per-campaign metrics (impressions, clicks, conversions, spend)
optionally scoped to a time range.
"""
from decimal import Decimal
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, select, cast, Integer
from datetime import datetime
from .models import Event

def campaign_report(session: Session, campaign_id: int, start: Optional[str], end: Optional[str]) -> Dict:
    """Return aggregated metrics for a campaign within optional time bounds."""
    q = select(
        func.sum(cast((Event.event_type == "impression"), Integer)).label("impressions"),
        func.sum(cast((Event.event_type == "click"), Integer)).label("clicks"),
        func.sum(cast((Event.event_type == "conversion"), Integer)).label("conversions"),
        func.coalesce(func.sum(Event.cost), 0).label("spend")
    ).where(Event.campaign_id == campaign_id)
    if start:
        try:
            sdt = datetime.fromisoformat(start)
            q = q.where(Event.ts >= sdt)
        except Exception:
            pass
    if end:
        try:
            edt = datetime.fromisoformat(end)
            q = q.where(Event.ts <= edt)
        except Exception:
            pass
    row = session.execute(q).one()
    return {
        "campaign_id": campaign_id,
        "impressions": int(row.impressions or 0),
        "clicks": int(row.clicks or 0),
        "conversions": int(row.conversions or 0),
        "spend": Decimal(str(row.spend or 0))
    }
