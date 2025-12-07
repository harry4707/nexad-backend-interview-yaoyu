from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class CampaignCreate(BaseModel):
    name: str
    pricing_model: Literal["cpm", "cpc", "cpa"]
    unit_price: Decimal = Field(gt=Decimal("0"))
    total_budget: Decimal = Field(gt=Decimal("0"))
    daily_budget: Decimal = Field(gt=Decimal("0"))
    freq_cap_impressions_per_day: Optional[int] = None

class CampaignOut(BaseModel):
    id: int
    name: str
    pricing_model: str
    unit_price: Decimal
    total_budget: Decimal
    daily_budget: Decimal
    spent_total: Decimal
    spent_today: Decimal
    freq_cap_impressions_per_day: Optional[int]
    active: bool
    class Config:
        from_attributes = True

class EventIn(BaseModel):
    campaign_id: int
    ad_id: Optional[str] = None
    user_id: str
    event_type: Literal["impression", "click", "conversion"]

class EventOut(BaseModel):
    id: int
    campaign_id: int
    ad_id: Optional[str]
    user_id: str
    event_type: str
    cost: Decimal
    ts: datetime
    class Config:
        from_attributes = True

class ReportQuery(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None

class CampaignReport(BaseModel):
    campaign_id: int
    impressions: int
    clicks: int
    conversions: int
    spend: Decimal
