# -*- coding: utf-8 -*-
"""Tests login + /auth/me + validation JWT."""
from __future__ import annotations

import time

from fastapi.testclient import TestClient

from tests.conftest import auth_header, signup_cabinet, signup_entreprise


def test_login_ok(client: TestClient) -> None:
    signup_entreprise(client, email="login@x.dz", nom="X")
    resp = client.post(
        "/auth/login", json={"email": "login@x.dz", "password": "motdepasse123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_mauvais_mdp_renvoie_401(client: TestClient) -> None:
    signup_entreprise(client, email="a@x.dz", nom="X")
    resp = client.post("/auth/login", json={"email": "a@x.dz", "password": "wrongpass1"})
    assert resp.status_code == 401


def test_login_user_inconnu_renvoie_401(client: TestClient) -> None:
    resp = client.post(
        "/auth/login", json={"email": "unknown@x.dz", "password": "motdepasse123"}
    )
    assert resp.status_code == 401


def test_me_entreprise_retourne_contexte_complet(client: TestClient) -> None:
    data = signup_entreprise(client, email="me@alpha.dz", nom="Alpha")
    resp = client.get("/auth/me", headers=auth_header(data["access_token"]))
    assert resp.status_code == 200
    me = resp.json()
    assert me["role"] == "patron"
    assert me["organisation_type"] == "entreprise"
    assert me["plan"] == "DECOUVERTE"
    assert me["entreprise_id"] == data["entreprise_id"]
    assert me["cabinet_id"] is None


def test_me_cabinet_retourne_plan_expert(client: TestClient) -> None:
    data = signup_cabinet(client, email="me@cabinet.dz", nom="Cab")
    resp = client.get("/auth/me", headers=auth_header(data["access_token"]))
    assert resp.status_code == 200
    me = resp.json()
    assert me["role"] == "consultant"
    assert me["organisation_type"] == "cabinet"
    assert me["plan"] == "EXPERT"
    assert me["cabinet_id"] == data["cabinet_id"]


def test_me_sans_token_renvoie_401(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401


def test_me_token_falsifie_renvoie_401(client: TestClient) -> None:
    data = signup_entreprise(client, email="f@x.dz", nom="X")
    bad_token = data["access_token"][:-4] + "AAAA"
    resp = client.get("/auth/me", headers=auth_header(bad_token))
    assert resp.status_code == 401


def test_me_token_expire_renvoie_401(client: TestClient) -> None:
    """G1 — Token expiré → 401."""
    from app.security import create_access_token

    signup_entreprise(client, email="exp@x.dz", nom="Exp")
    # On forge un token déjà expiré
    token = create_access_token(
        user_id=1,
        organisation_id=1,
        role="patron",
        organisation_type="entreprise",
        expires_hours=-1,  # expiration dans le passé
    )
    resp = client.get("/auth/me", headers=auth_header(token))
    assert resp.status_code == 401
    assert "token_expired" in resp.json()["detail"]
