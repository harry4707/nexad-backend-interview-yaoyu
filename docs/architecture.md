# Minimal Ad Backend Architecture

## Components
1. API service: FastAPI providing endpoints for events, campaigns, reports
2. PostgreSQL: durable storage for campaigns and events
3. Redis: atomic counters for per-user daily frequency capping

## Core Logic
- Budget control uses row-level locks with `SELECT ... FOR UPDATE` to prevent race conditions and enforces daily/total caps within a transaction
- Frequency capping uses a Redis Lua script performing atomic check-and-increment with day-based TTL
- Pricing model determines spend: CPM per impression, CPC per click, CPA per conversion

## Concurrency
- Events are processed by acquiring a campaign row lock, resetting daily spend when the date changes, evaluating caps, then writing the event and committing
- Frequency capping key: `freq:{campaign_id}:{user_id}:{YYYY-MM-DD}:{event_type}` with TTL to end of day

## Data Model
- Campaign: pricing_model, unit_price, total_budget, daily_budget, spent_total, spent_today, last_spend_reset, freq_cap_impressions_per_day
- Event: campaign_id, user_id, ad_id, event_type, cost, ts

## Failure Modes
- BudgetExceeded: HTTP 402 for spend-blocking
- Frequency exceeded: HTTP 429

## Notes
- Daily spend resets lazily on first event of the new day
- Only events matching the campaign pricing model incur cost
