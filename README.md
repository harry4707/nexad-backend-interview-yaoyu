# Minimal Ad Backend (FastAPI)

This repository contains a minimal yet production-minded advertisement backend implemented in Python using FastAPI, SQLAlchemy, and Redis. It supports event ingestion (impression/click/conversion), real-time budget control, frequency capping, and reporting APIs.

All application code and comments are written in English. Documentation here aims to make local startup straightforward.

## Project Structure
- `adserver/app/` – FastAPI app, models, services, routers
- `adserver/requirements.txt` – runtime dependencies
- `adserver/requirements-dev.txt` – development/test dependencies
- `adserver/Dockerfile` – container image for the API service
- `docker-compose.yml` – full local stack (API + Postgres + Redis + test service)
- `docs/architecture.md` – architecture and design notes
- `docs/api.md` – API endpoints specification
- `adserver/tests/` – unit and end-to-end tests

## Prerequisites
- Option A: Docker + Docker Compose (recommended)
- Option B: Native Python (3.11 or 3.12 recommended)
  - Note: Python 3.14 may require building `pydantic-core` via Rust and can fail in some environments. Prefer 3.11/3.12 or use Docker.

## Quick Start (Docker Compose)
1. Build and start the full stack:
   - `docker compose up --build`
2. API will be available at:
   - `http://localhost:8000`
3. Sample calls:
   - Create a campaign:
     - `curl -X POST http://localhost:8000/campaigns/ -H 'Content-Type: application/json' -d '{"name":"demo","pricing_model":"cpm","unit_price":"10","total_budget":"5","daily_budget":"1","freq_cap_impressions_per_day":2}'`
   - Send an impression:
     - `curl -X POST http://localhost:8000/events/ -H 'Content-Type: application/json' -d '{"campaign_id":1,"user_id":"u1","event_type":"impression"}'`
   - Get report:
     - `curl http://localhost:8000/report/campaign/1`

### Run tests in Docker
- `docker compose run --rm tests`

## Local Development (without Docker)
This mode is convenient for editing and quick unit tests. There are two paths:

### A. Testing mode (SQLite + fakeredis)
1. Create a virtual environment and install dependencies:
   - `cd adserver`
   - `python3 -m venv .venv && . .venv/bin/activate`
   - `pip install -r requirements.txt -r requirements-dev.txt`
2. Run unit tests:
   - `APP_TESTING=1 PYTHONPATH=. pytest -q tests/unit`
3. Start the API (uses SQLite and fakeredis by default when `APP_TESTING=1`):
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### B. Full stack locally (API native + DB/Redis via containers)
1. Start Postgres and Redis via Compose:
   - `docker compose up -d db redis`
2. Create venv and install dependencies:
   - `cd adserver`
   - `python3 -m venv .venv && . .venv/bin/activate`
   - `pip install -r requirements.txt`
3. Configure environment variables:
   - `export DB_URL=postgresql+psycopg://ad:ad@localhost:5432/adserver`
   - `export REDIS_URL=redis://localhost:6379/0`
   - `unset APP_TESTING` (ensure testing mode is off)
4. Start the API:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Configuration
- `APP_TESTING`
  - `1` enables testing mode: SQLite and fakeredis are used automatically
  - unset/`0` uses configured DB and Redis
- `DB_URL`
  - SQLAlchemy database URL, defaults to `postgresql+psycopg://ad:ad@db:5432/adserver` in containers
  - Example for local native run: `postgresql+psycopg://ad:ad@localhost:5432/adserver`
- `REDIS_URL`
  - Redis connection URL, defaults to `redis://redis:6379/0` in containers
  - Example for local native run: `redis://localhost:6379/0`

## Testing
- Unit tests:
  - `APP_TESTING=1 PYTHONPATH=. pytest -q adserver/tests/unit` (run from repo root)
- End-to-End tests:
  - `docker compose run --rm tests`

## API Reference
- See `docs/api.md` for endpoint details and error codes
- See `docs/architecture.md` for concurrency and data model notes

## Common Issues
- Python 3.14 build errors for `pydantic-core`:
  - Prefer Python 3.11/3.12 or run via Docker
- `docker: command not found`:
  - Install Docker Desktop and ensure `docker`/`docker compose` are in PATH

## Commit Guidelines
- Keep commits small and descriptive, e.g.:
  - `feat(services): implement frequency capping Lua and fallback`
  - `feat(api): add event ingestion endpoint`
  - `test(e2e): add end-to-end flow test`
  - `docs: add architecture and API`

## License
Internal interview project; distribution restricted.
nexad_take-home-Assignment
