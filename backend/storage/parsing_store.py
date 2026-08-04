"""Persistent storage for parsing results."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.parsers.ast_models import ProjectParsingResult
from storage.database import get_session_factory, init_db
from storage.models import RepositoryRow

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ParsingStore:
    """Persistent storage for parsing results using SQLite."""

    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        self._session_factory = session_factory or get_session_factory()
        if session_factory is None:
            init_db()

    def _sessions(self) -> sessionmaker[Session]:
        return self._session_factory

    def save(self, repository_id: str, parsing_result: ProjectParsingResult) -> None:
        """Save parsing result to database."""
        logger.info("=" * 80)
        logger.info("PARSING_STORE: save() called")
        logger.info("=" * 80)
        logger.info("Repository ID: %s", repository_id)
        logger.info("Parsing result files: %d", len(parsing_result.files))
        logger.info("Parsing result total classes: %d", sum(len(f.classes) for f in parsing_result.files))
        logger.info("Parsing result total functions: %d", sum(len(f.functions) for f in parsing_result.files))
        
        try:
            parsing_json = parsing_result.model_dump_json()
            with self._sessions()() as session:
                row = session.get(RepositoryRow, repository_id)
                if row is None:
                    logger.warning("PARSING_STORE: Repository %s not found, creating row", repository_id)
                    row = RepositoryRow(
                        upload_id=repository_id,
                        repository_id=repository_id,
                        extraction_path="",
                        created_at=_utcnow(),
                        updated_at=_utcnow(),
                    )
                    session.add(row)
                
                row.parsing_result_json = parsing_json
                row.parsed_at = _utcnow()
                row.updated_at = _utcnow()
                session.commit()
                
            logger.info("PARSING_STORE: Successfully saved parsing result for %s", repository_id)
            logger.info("=" * 80)
        except Exception as e:
            logger.error("PARSING_STORE: Failed to save parsing result for %s: %s", repository_id, e, exc_info=True)
            raise

    def load(self, repository_id: str) -> Optional[ProjectParsingResult]:
        """Load parsing result from database."""
        logger.info("=" * 80)
        logger.info("PARSING_STORE: load() called")
        logger.info("=" * 80)
        logger.info("Repository ID: %s", repository_id)
        
        try:
            with self._sessions()() as session:
                row = session.get(RepositoryRow, repository_id)
                if row is None or row.parsing_result_json is None:
                    logger.info("PARSING_STORE: No parsing result found for %s", repository_id)
                    logger.info("=" * 80)
                    return None
                
                parsing_result = ProjectParsingResult.model_validate_json(row.parsing_result_json)
                logger.info("PARSING_STORE: Loaded parsing result for %s", repository_id)
                logger.info("  Files: %d", len(parsing_result.files))
                logger.info("  Classes: %d", sum(len(f.classes) for f in parsing_result.files))
                logger.info("  Functions: %d", sum(len(f.functions) for f in parsing_result.files))
                logger.info("=" * 80)
                return parsing_result
        except Exception as e:
            logger.error("PARSING_STORE: Failed to load parsing result for %s: %s", repository_id, e, exc_info=True)
            logger.info("=" * 80)
            return None

    def delete(self, repository_id: str) -> None:
        """Delete parsing result from database."""
        logger.info("PARSING_STORE: Deleting parsing result for %s", repository_id)
        
        try:
            with self._sessions()() as session:
                row = session.get(RepositoryRow, repository_id)
                if row is not None:
                    row.parsing_result_json = None
                    row.parsed_at = None
                    row.updated_at = _utcnow()
                    session.commit()
                    logger.info("PARSING_STORE: Successfully deleted parsing result for %s", repository_id)
        except Exception as e:
            logger.error("PARSING_STORE: Failed to delete parsing result for %s: %s", repository_id, e, exc_info=True)
            raise

    def exists(self, repository_id: str) -> bool:
        """Check if parsing result exists for repository."""
        try:
            with self._sessions()() as session:
                row = session.get(RepositoryRow, repository_id)
                return row is not None and row.parsing_result_json is not None
        except Exception as e:
            logger.error("PARSING_STORE: Failed to check parsing result for %s: %s", repository_id, e)
            return False


# Global instance
parsing_store = ParsingStore()
