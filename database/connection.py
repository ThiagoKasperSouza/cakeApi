import time
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
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


def execute_seed_sql(connection: Connection) -> None:
    seed_sql_path = Path(__file__).resolve().parents[1] / "insert_into_db.sql"
    seed_sql = seed_sql_path.read_text(encoding="utf-8")
    for statement in seed_sql.split(";"):
        if statement.strip():
            connection.exec_driver_sql(statement)


def init_db(retries: int = 10, delay_seconds: float = 2.0) -> None:
    from models import budget, category, product, team_member, user  # noqa: F401

    for attempt in range(1, retries + 1):
        try:
            with engine.begin() as connection:
                Base.metadata.create_all(bind=connection)
                execute_seed_sql(connection)
            return
        except Exception:
            if attempt == retries:
                raise
            time.sleep(delay_seconds)
