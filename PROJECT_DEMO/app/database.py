# -*- coding: utf-8 -*-
"""Configuration SQLAlchemy 2.x — engine, session, dépendance FastAPI."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings


def _build_engine() -> Engine:
    settings = get_settings()
    connect_args: dict = {}
    if settings.is_sqlite:
        connect_args["check_same_thread"] = False
    return create_engine(
        settings.database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        future=True,
    )


engine: Engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI — fournit une session, la ferme après requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
