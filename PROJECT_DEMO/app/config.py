# -*- coding: utf-8 -*-
"""Configuration applicative via pydantic-settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration chargée depuis l'environnement / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SOUMISSION_",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = "development"
    jwt_secret: str = Field(default="dev-insecure-secret-do-not-use-in-prod")
    jwt_expire_hours: int = 24
    jwt_algorithm: str = "HS256"

    database_url: str = Field(
        default="sqlite:///./soumission_dev.db",
        validation_alias="DATABASE_URL",
    )
    storage_root: str = Field(default="./storage", validation_alias="STORAGE_ROOT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    @property
    def storage_path(self) -> Path:
        p = Path(self.storage_root).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuration."""
    return Settings()
