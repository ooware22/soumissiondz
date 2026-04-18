# -*- coding: utf-8 -*-
"""Tests d'inscription des 3 profils (Cas 1 entreprise, Cas 2 cabinet)."""
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import signup_cabinet, signup_entreprise


def test_signup_entreprise_cree_org_entreprise_et_patron(client: TestClient) -> None:
    data = signup_entreprise(client, email="patron@alpha-btph.dz", nom="Alpha BTPH")
    assert data["organisation_type"] == "entreprise"
    assert data["entreprise_id"] is not None
    assert data["cabinet_id"] is None
    assert data["access_token"]
    assert data["expires_in"] == 24 * 3600


def test_signup_cabinet_cree_org_cabinet_et_consultant(client: TestClient) -> None:
    data = signup_cabinet(client, email="mourad@cabinet.dz", nom="Cabinet Mourad")
    assert data["organisation_type"] == "cabinet"
    assert data["cabinet_id"] is not None
    assert data["entreprise_id"] is None
    assert data["access_token"]


def test_signup_email_duplique_renvoie_409(client: TestClient) -> None:
    signup_entreprise(client, email="dup@x.dz", nom="Xx")
    resp = client.post(
        "/signup/entreprise",
        json={
            "email": "dup@x.dz",
            "password": "motdepasse123",
            "username": "dup",
            "nom_entreprise": "Yy",
        },
    )
    assert resp.status_code == 409


def test_signup_password_trop_court_renvoie_422(client: TestClient) -> None:
    resp = client.post(
        "/signup/entreprise",
        json={
            "email": "short@x.dz",
            "password": "abc",
            "username": "x",
            "nom_entreprise": "X",
        },
    )
    assert resp.status_code == 422


def test_signup_forme_juridique_invalide_renvoie_422(client: TestClient) -> None:
    resp = client.post(
        "/signup/entreprise",
        json={
            "email": "bad@x.dz",
            "password": "motdepasse123",
            "username": "x",
            "nom_entreprise": "X",
            "forme_juridique": "LTD",
        },
    )
    assert resp.status_code == 422


def test_signup_cabinet_email_dup_avec_compte_entreprise(client: TestClient) -> None:
    """Un email déjà pris côté entreprise ne peut pas être réutilisé côté cabinet."""
    signup_entreprise(client, email="cross@x.dz", nom="Ent")
    resp = client.post(
        "/signup/cabinet",
        json={
            "email": "cross@x.dz",
            "password": "motdepasse123",
            "username": "cc",
            "nom_cabinet": "Cab",
            "consultant_principal": "Cc",
        },
    )
    assert resp.status_code == 409
