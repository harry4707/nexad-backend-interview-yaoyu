from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from adserver.app.db import Base
from adserver.app.models import Campaign
from adserver.app.services.budget import apply_budget, BudgetExceeded
from datetime import date

def setup_session():
    eng = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Session = sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=eng)
    return Session()

def test_cpm_impression_spend_and_limits():
    s = setup_session()
    c = Campaign(name="c1", pricing_model="cpm", unit_price=Decimal("10"), total_budget=Decimal("1"), daily_budget=Decimal("1"))
    s.add(c)
    s.commit()
    s.refresh(c)
    cost = apply_budget(s, c.id, "impression", date.today())
    assert cost == Decimal("0.01")
    s.commit()
    c = s.query(Campaign).get(c.id)
    assert Decimal(str(c.spent_today)) == Decimal("0.01")
    c.daily_budget = Decimal("0.01")
    s.add(c)
    s.commit()
    try:
        apply_budget(s, c.id, "impression", date.today())
        assert False
    except BudgetExceeded:
        s.rollback()

