from datetime import datetime, timezone
import fakeredis
from adserver.app.services.frequency import check_and_increment

def test_freq_capping_daily():
    r = fakeredis.FakeRedis(decode_responses=True)
    now = datetime.now(timezone.utc)
    cap = 2
    assert check_and_increment(r, 1, "u", "impression", cap, now) is True
    assert check_and_increment(r, 1, "u", "impression", cap, now) is True
    assert check_and_increment(r, 1, "u", "impression", cap, now) is False

