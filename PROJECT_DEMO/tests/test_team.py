# -*- coding: utf-8 -*-
"""Tests de l'endpoint /team — invitation et listing."""
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header, signup_entreprise


def test_patron_peut_inviter_les_3_roles(client: TestClient) -> None:
    data = signup_entreprise(client, email="boss@x.dz", nom="Boss")
    h = auth_header(data["access_token"])

    for role in ("validateur", "preparateur", "lecteur"):
        resp = client.post(
            "/team/invite",
            headers=h,
            json={
                "email": f"{role}@x.dz",
                "username": role,
                "password": "motdepasse123",
                "role": role,
            },
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["role"] == role

    # Le listing doit contenir le patron + 3 membres
    members = client.get("/team", headers=h).json()
    assert len(members) == 4


def test_invitation_role_inconnu_renvoie_422(client: TestClient) -> None:
    data = signup_entreprise(client, email="x@x.dz", nom="X")
    resp = client.post(
        "/team/invite",
        headers=auth_header(data["access_token"]),
        json={
            "email": "n@x.dz",
            "username": "n",
            "password": "motdepasse123",
            "role": "admin_plateforme",
        },
    )
    assert resp.status_code == 422


def test_invitation_email_existant_renvoie_409(client: TestClient) -> None:
    data = signup_entreprise(client, email="p@x.dz", nom="PP")
    h = auth_header(data["access_token"])
    client.post(
        "/team/invite",
        headers=h,
        json={
            "email": "dup@x.dz",
            "username": "dd",
            "password": "motdepasse123",
            "role": "lecteur",
        },
    ).raise_for_status()
    resp2 = client.post(
        "/team/invite",
        headers=h,
        json={
            "email": "dup@x.dz",
            "username": "d2",
            "password": "motdepasse123",
            "role": "lecteur",
        },
    )
    assert resp2.status_code == 409


def test_health_endpoint_public(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
