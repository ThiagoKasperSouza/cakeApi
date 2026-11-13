import time
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings
from database.base import Base

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(retries: int = 10, delay_seconds: float = 2.0) -> None:
    from models import budget, category, product, team_member, user  # noqa: F401

    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except Exception:
            if attempt == retries:
                raise
            time.sleep(delay_seconds)
