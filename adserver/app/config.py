import os
from datetime import datetime, timezone

class Config:
    APP_NAME = os.getenv("APP_NAME", "adserver")
    APP_TESTING = os.getenv("APP_TESTING", "0") == "1"
    DB_URL = os.getenv("DB_URL") or ("sqlite:///./adserver.db" if APP_TESTING else os.getenv("DB_URL", "postgresql+psycopg://ad:ad@db:5432/adserver"))
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0" if not APP_TESTING else os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    TIMEZONE = timezone.utc

def utc_now():
    return datetime.now(Config.TIMEZONE)
