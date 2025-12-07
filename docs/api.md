# API

## Create Campaign
- `POST /campaigns/`
- Body: `{ name, pricing_model(cpm|cpc|cpa), unit_price, total_budget, daily_budget, freq_cap_impressions_per_day? }`
- Returns: campaign

## Get Campaign
- `GET /campaigns/{campaign_id}`

## Ingest Event
- `POST /events/`
- Body: `{ campaign_id, ad_id?, user_id, event_type(impression|click|conversion) }`
- Returns: event with computed `cost`
- Errors: `404` missing campaign, `429` frequency cap exceeded, `402` budget exceeded

## Campaign Report
- `GET /report/campaign/{campaign_id}?start=ISO8601&end=ISO8601`
- Returns aggregated counts and spend
