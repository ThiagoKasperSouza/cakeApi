from collections.abc import Generator
from pathlib import Path
import time
import unicodedata

from sqlalchemy import Integer, create_engine, inspect, text
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


def migrate_integer_category_ids(connection: Connection) -> None:
    if connection.dialect.name != "postgresql":
        return

    category_id_column = next(
        column for column in inspect(connection).get_columns("categories") if column["name"] == "id"
    )
    if not isinstance(category_id_column["type"], Integer):
        return

    categories = connection.execute(text("SELECT id, label FROM categories ORDER BY id")).all()
    known_ids = {
        "bolos": "cakes",
        "cakes": "cakes",
        "cupcakes": "cupcakes",
        "cookies": "cookies",
        "cafes": "coffee",
        "coffee": "coffee",
    }
    used_ids: set[str] = set()
    category_ids: list[dict[str, int | str]] = []
    for old_id, label in categories:
        normalized_label = (
            unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode().casefold()
        )
        new_id = known_ids.get(normalized_label, f"legacy-{old_id}")
        if new_id in used_ids:
            new_id = f"legacy-{old_id}"
        used_ids.add(new_id)
        category_ids.append({"old_id": old_id, "new_id": new_id})

    preparer = connection.dialect.identifier_preparer
    for foreign_key in inspect(connection).get_foreign_keys("products"):
        if foreign_key["referred_table"] == "categories":
            constraint = preparer.quote(foreign_key["name"])
            connection.exec_driver_sql(f"ALTER TABLE products DROP CONSTRAINT {constraint}")

    connection.exec_driver_sql(
        "CREATE TEMP TABLE category_id_map "
        "(old_id BIGINT PRIMARY KEY, new_id VARCHAR(32) NOT NULL) ON COMMIT DROP"
    )
    if category_ids:
        connection.execute(
            text("INSERT INTO category_id_map (old_id, new_id) VALUES (:old_id, :new_id)"),
            category_ids,
        )

    connection.exec_driver_sql("ALTER TABLE products ADD COLUMN category_id_new VARCHAR(32)")
    connection.exec_driver_sql(
        "UPDATE products AS p SET category_id_new = m.new_id "
        "FROM category_id_map AS m WHERE p.category_id = m.old_id"
    )
    orphaned_products = connection.scalar(
        text("SELECT count(*) FROM products WHERE category_id_new IS NULL")
    )
    if orphaned_products:
        raise RuntimeError(f"Cannot migrate {orphaned_products} products with missing categories")

    connection.exec_driver_sql("ALTER TABLE categories ALTER COLUMN id DROP DEFAULT")
    connection.exec_driver_sql(
        "ALTER TABLE categories ALTER COLUMN id TYPE VARCHAR(32) USING id::text"
    )
    connection.exec_driver_sql(
        "UPDATE categories AS c SET id = m.new_id "
        "FROM category_id_map AS m WHERE c.id = m.old_id::text"
    )
    connection.exec_driver_sql("ALTER TABLE products DROP COLUMN category_id")
    connection.exec_driver_sql(
        "ALTER TABLE products RENAME COLUMN category_id_new TO category_id"
    )
    connection.exec_driver_sql(
        "ALTER TABLE products ADD CONSTRAINT products_category_id_fkey "
        "FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE"
    )
    connection.exec_driver_sql(
        "CREATE INDEX ix_products_category_id ON products (category_id)"
    )


def init_db(retries: int = 10, delay_seconds: float = 2.0) -> None:
    from models import budget, category, product, team_member, user  # noqa: F401

    for attempt in range(1, retries + 1):
        try:
            with engine.begin() as connection:
                Base.metadata.create_all(bind=connection)
                migrate_integer_category_ids(connection)
                execute_seed_sql(connection)
            return
        except Exception:
            if attempt == retries:
                raise
            time.sleep(delay_seconds)
