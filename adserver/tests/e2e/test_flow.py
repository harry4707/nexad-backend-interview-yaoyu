import os
os.environ["APP_TESTING"] = "1"
from fastapi.testclient import TestClient
from adserver.app.main import app

client = TestClient(app)

def test_end_to_end_campaign_events_and_report():
    c = client.post("/campaigns/", json={
        "name": "demo",
        "pricing_model": "cpm",
        "unit_price": "10",
        "total_budget": "5",
        "daily_budget": "1",
        "freq_cap_impressions_per_day": 2
    }).json()
    cid = c["id"]
    r1 = client.post("/events/", json={"campaign_id": cid, "user_id": "u1", "event_type": "impression"})
    assert r1.status_code == 200
    r2 = client.post("/events/", json={"campaign_id": cid, "user_id": "u1", "event_type": "impression"})
    assert r2.status_code == 200
    r3 = client.post("/events/", json={"campaign_id": cid, "user_id": "u1", "event_type": "impression"})
    assert r3.status_code == 429
    rep = client.get(f"/report/campaign/{cid}").json()
    assert rep["impressions"] == 2
    assert str(rep["spend"]).startswith("0.02")

