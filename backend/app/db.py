from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import settings

engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"options": "-c default_transaction_read_only=on"},
)


def get_db() -> Generator[Engine, None, None]:
    yield engine


def fetch_all(sql: str, params: dict | None = None) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]
