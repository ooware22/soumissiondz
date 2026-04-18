# -*- coding: utf-8 -*-
"""Fixtures pytest — DB isolee par test, client FastAPI, helpers d'inscription."""
from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Avant tout import app : forcer un secret JWT stable et une DB SQLite de test
os.environ["SOUMISSION_JWT_SECRET"] = "test-secret-key-for-pytest-only-do-not-use"
os.environ["SOUMISSION_ENV"] = "test"

_TMP = Path(tempfile.gettempdir()) / "soumission_dz_tests"
_TMP.mkdir(exist_ok=True)


@pytest.fixture(scope="function")
def db_url(tmp_path_factory) -> str:
    """Fichier SQLite jetable par test, pour isolation réelle entre tests."""
    db_file = tmp_path_factory.mktemp("db") / "test.sqlite"
    url = f"sqlite:///{db_file}"
    os.environ["DATABASE_URL"] = url
    return url


@pytest.fixture(scope="function")
def client(db_url: str) -> Iterator[TestClient]:
    """TestClient FastAPI avec schéma créé via la metadata (équivalent migrations Alembic)."""
    # Imports APRES avoir fixé DATABASE_URL pour que le singleton Settings voie la bonne URL
    from app.config import get_settings

    get_settings.cache_clear()

    # Reconstruire l'engine avec la nouvelle URL
    from app import database as db_mod

    new_engine = create_engine(db_url, connect_args={"check_same_thread": False}, future=True)
    db_mod.engine = new_engine
    db_mod.SessionLocal = sessionmaker(
        bind=new_engine, autoflush=False, autocommit=False, expire_on_commit=False
    )

    # Créer le schéma
    from app.models import Base

    Base.metadata.create_all(bind=new_engine)

    from app.main import create_app

    app = create_app()
    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=new_engine)
    new_engine.dispose()


# ---------------------------------------------------------------------------
# Helpers — inscription/login réutilisables
# ---------------------------------------------------------------------------


def _pad(v: str, minlen: int = 2) -> str:
    return v if len(v) >= minlen else (v + "x" * (minlen - len(v)))


def signup_entreprise(client: TestClient, *, email: str, nom: str, password: str = "motdepasse123") -> dict:
    nom = _pad(nom)
    resp = client.post(
        "/signup/entreprise",
        json={
            "email": email,
            "password": password,
            "username": _pad(nom.split()[0]),
            "nom_entreprise": nom,
            "forme_juridique": "SARL",
            "wilaya_code": "16",
            "wilaya_nom": "Alger",
            "secteur": "BTPH",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def signup_cabinet(client: TestClient, *, email: str, nom: str, password: str = "motdepasse123") -> dict:
    nom = _pad(nom)
    resp = client.post(
        "/signup/cabinet",
        json={
            "email": email,
            "password": password,
            "username": _pad(nom.split()[0]),
            "nom_cabinet": nom,
            "consultant_principal": f"Consultant {nom}",
            "wilaya_code": "16",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
