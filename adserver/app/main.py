"""FastAPI application entry point.

Initializes database schema and mounts routers for campaigns, events, and
reports.
"""
from fastapi import FastAPI
from .db import init_db
from .routers import campaigns, events, reports

app = FastAPI(title="AdServer")
init_db()
app.include_router(campaigns.router)
app.include_router(events.router)
app.include_router(reports.router)
