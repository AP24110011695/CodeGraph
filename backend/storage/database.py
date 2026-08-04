"""SQLite engine and session helpers for CodeGraph persistence."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine, event, text, Inspector
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

DEFAULT_DB_PATH = Path("storage") / "codegraph.db"

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_db_path() -> Path:
    """Resolve SQLite file path (override with CODEGRAPH_DB_PATH)."""
    if settings.CODEGRAPH_DB_PATH:
        return Path(settings.CODEGRAPH_DB_PATH)
    override = os.environ.get("CODEGRAPH_DB_PATH")
    if override:
        return Path(override)
    return DEFAULT_DB_PATH


def get_engine(db_path: Path | str | None = None) -> Engine:
    """Return a process-wide SQLAlchemy engine (creates DB file if needed)."""
    global _engine, _SessionLocal
    if db_path is not None:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(
            f"sqlite:///{path.resolve().as_posix()}",
            connect_args={"check_same_thread": False},
            future=True,
        )

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

    if _engine is None:
        path = get_db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{path.resolve().as_posix()}",
            connect_args={"check_same_thread": False},
            future=True,
        )

        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def get_session_factory(db_path: Path | str | None = None) -> sessionmaker[Session]:
    """Return a session factory bound to the default or provided engine."""
    global _SessionLocal
    if db_path is not None:
        engine = get_engine(db_path)
        return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    if _SessionLocal is None:
        get_engine()
    assert _SessionLocal is not None
    return _SessionLocal


def _add_column_if_missing(engine: Engine, table: str, column: str, column_def: str) -> None:
    """Helper to add a column if it does not exist in the table."""
    with engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA table_info({table})"))
        columns = [row[1] for row in result]
        if column not in columns:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {column_def}"))
            conn.commit()


def init_db(db_path: Path | str | None = None) -> Engine:
    """Create tables if they do not exist, and run inline column migrations."""
    from storage.models import Base

    engine = get_engine(db_path)
    Base.metadata.create_all(bind=engine)

    # Inline migration: add new columns to existing databases that pre-date them.
    # SQLite does not support IF NOT EXISTS on ALTER TABLE, so we check PRAGMA first.
    _add_column_if_missing(engine, "repositories", "total_folders", "INTEGER NOT NULL DEFAULT 0")
    _add_column_if_missing(engine, "repositories", "zip_size_bytes", "INTEGER NOT NULL DEFAULT 0")
    
    # Phase 5.5: Add parsing result columns
    _add_column_if_missing(engine, "repositories", "parsing_result_json", "TEXT")
    _add_column_if_missing(engine, "repositories", "parsed_at", "DATETIME")

    return engine


def reset_engine() -> None:
    """Drop cached engine (tests only)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
