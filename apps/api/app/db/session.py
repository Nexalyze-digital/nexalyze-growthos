from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _connect_args(database_url: str) -> dict[str, bool]:
    return {"check_same_thread": False} if database_url.startswith("sqlite") else {}


def _engine_options(database_url: str) -> dict[str, object]:
    options: dict[str, object] = {
        "connect_args": _connect_args(database_url),
        "future": True,
        "pool_pre_ping": settings.database_pool_pre_ping,
    }
    if not database_url.startswith("sqlite"):
        options["pool_size"] = settings.database_pool_size
        options["max_overflow"] = settings.database_max_overflow
    return options


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    path = Path(database_url.replace("sqlite:///", "", 1))
    if path != Path(":memory:"):
        path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_parent(settings.database_url)
engine = create_engine(
    settings.database_url,
    **_engine_options(settings.database_url),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
