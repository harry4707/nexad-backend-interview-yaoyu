from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    pricing_model = Column(Enum("cpm", "cpc", "cpa", name="pricing_model"), nullable=False)
    unit_price = Column(Numeric(12, 6), nullable=False)
    total_budget = Column(Numeric(12, 2), nullable=False)
    daily_budget = Column(Numeric(12, 2), nullable=False)
    spent_total = Column(Numeric(12, 2), nullable=False, server_default="0")
    spent_today = Column(Numeric(12, 2), nullable=False, server_default="0")
    last_spend_reset = Column(Date, nullable=True)
    freq_cap_impressions_per_day = Column(Integer, nullable=True)
    active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    events = relationship("Event", back_populates="campaign")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    ad_id = Column(String(255), nullable=True)
    user_id = Column(String(255), nullable=False)
    event_type = Column(Enum("impression", "click", "conversion", name="event_type"), nullable=False)
    cost = Column(Numeric(12, 6), nullable=False, server_default="0")
    ts = Column(DateTime(timezone=True), server_default=func.now())
    campaign = relationship("Campaign", back_populates="events")
