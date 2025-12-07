"""Budget control and pricing.

Enforces daily and total budget caps with transactional row-level locking.
Costs are computed based on pricing model (CPM/CPC/CPA).
"""
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from datetime import date
from ..models import Campaign
from sqlalchemy import select

def event_cost(pricing_model: str, unit_price: Decimal, event_type: str) -> Decimal:
    """Return per-event cost according to pricing model.

    CPM: cost per impression is unit_price/1000; CPC: per click; CPA: per conversion.
    """
    if pricing_model == "cpm" and event_type == "impression":
        return (unit_price / Decimal("1000")).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    if pricing_model == "cpc" and event_type == "click":
        return unit_price
    if pricing_model == "cpa" and event_type == "conversion":
        return unit_price
    return Decimal("0")

class BudgetExceeded(Exception):
    """Raised when daily or total budget would be exceeded."""
    pass

def apply_budget(session: Session, campaign_id: int, event_type: str, now_date: date) -> Decimal:
    """Apply spend atomically and return event cost.

    Locks the campaign row, resets daily spend on date change, checks caps,
    updates spend totals, and returns the computed cost.
    """
    bind = session.get_bind()
    stmt = select(Campaign).where(Campaign.id == campaign_id)
    if bind and getattr(bind.dialect, "name", "") != "sqlite":
        stmt = stmt.with_for_update()
    campaign = session.execute(stmt).scalar_one()
    if not campaign.active:
        raise BudgetExceeded()
    if campaign.last_spend_reset != now_date:
        campaign.spent_today = Decimal("0")
        campaign.last_spend_reset = now_date
    cost = event_cost(campaign.pricing_model, Decimal(str(campaign.unit_price)), event_type)
    new_daily = Decimal(str(campaign.spent_today)) + cost
    new_total = Decimal(str(campaign.spent_total)) + cost
    if campaign.daily_budget is not None and new_daily > Decimal(str(campaign.daily_budget)):
        raise BudgetExceeded()
    if campaign.total_budget is not None and new_total > Decimal(str(campaign.total_budget)):
        raise BudgetExceeded()
    campaign.spent_today = new_daily
    campaign.spent_total = new_total
    session.add(campaign)
    return cost
