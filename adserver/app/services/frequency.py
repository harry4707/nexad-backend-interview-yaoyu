from datetime import datetime, timedelta
from typing import Optional
from redis import Redis
from redis.exceptions import ResponseError

def seconds_until_end_of_day(now: datetime) -> int:
    """Compute TTL seconds until end of the day in the same timezone as `now`."""
    end = datetime(year=now.year, month=now.month, day=now.day, tzinfo=now.tzinfo) + timedelta(days=1)
    return int((end - now).total_seconds())

LUA_CAP_SCRIPT = """
local key = KEYS[1]
local cap = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local current = redis.call('GET', key)
if current == false then
  redis.call('SET', key, 1, 'EX', ttl)
  return 1
else
  local val = tonumber(current)
  if val >= cap then
    return cap + 1
  else
    val = redis.call('INCR', key)
    return val
  end
end
"""

def check_and_increment(redis: Redis, campaign_id: int, user_id: str, event_type: str, cap: Optional[int], now: datetime) -> bool:
    """Check cap and increment atomically.

    Returns True when under cap and increments, False when cap exceeded.
    """
    if not cap:
        return True
    ttl = seconds_until_end_of_day(now)
    k = f"freq:{campaign_id}:{user_id}:{now.date()}:{event_type}"
    try:
        val = redis.eval(LUA_CAP_SCRIPT, 1, k, cap, ttl)
        return int(val) <= cap
    except ResponseError:
        pipe = redis.pipeline()
        while True:
            try:
                pipe.watch(k)
                cur = redis.get(k)
                if cur is None:
                    pipe.multi()
                    pipe.set(k, 1, ex=ttl)
                    pipe.execute()
                    return True
                v = int(cur)
                if v >= cap:
                    pipe.unwatch()
                    return False
                pipe.multi()
                pipe.incr(k)
                pipe.execute()
                return True
            except Exception:
                continue
"""Frequency capping service.

Provides atomic per-user daily caps using Redis. Uses Lua `EVAL` when
available, falling back to optimistic transactions with `WATCH/MULTI/EXEC`.
Keys are scoped per campaign, user, date, and event type.
"""
