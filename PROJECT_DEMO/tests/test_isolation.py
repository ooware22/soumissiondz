# -*- coding: utf-8 -*-
"""Tests d'isolation cross-tenant — garanties G2, G3, G4 du contrat de sécurité.

Ces tests sont OBLIGATOIRES pour merger un endpoint métier. Lot 1 : vérifier
l'étanchéité sur les endpoints /team (le seul endpoint métier Lot 1 qui
manipule des objets scopés).
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header, signup_cabinet, signup_entreprise


def _two_entreprises(client: TestClient) -> tuple[dict, dict]:
    """Crée 2 entreprises Cas 1 distinctes."""
    a = signup_entreprise(client, email="a@alpha.dz", nom="Alpha BTPH")
    b = signup_entreprise(client, email="b@bravo.dz", nom="Bravo BTPH")
    return a, b


def test_team_invite_ne_fuit_pas_vers_autre_entreprise(client: TestClient) -> None:
    """G3 — organisation_id du payload ignoré, écrasé serveur-side.

    Si le patron de A invite un membre, il atterrit dans A — pas dans B.
    """
    a, b = _two_entreprises(client)

    resp = client.post(
        "/team/invite",
        headers=auth_header(a["access_token"]),
        json={
            "email": "membre1@alpha.dz",
            "username": "m1",
            "password": "motdepasse123",
            "role": "preparateur",
        },
    )
    assert resp.status_code == 201

    # Le patron de B ne doit pas voir ce membre
    resp_b = client.get("/team", headers=auth_header(b["access_token"]))
    assert resp_b.status_code == 200
    emails_b = {m["email"] for m in resp_b.json()}
    assert "membre1@alpha.dz" not in emails_b

    # Le patron de A le voit
    resp_a = client.get("/team", headers=auth_header(a["access_token"]))
    emails_a = {m["email"] for m in resp_a.json()}
    assert "membre1@alpha.dz" in emails_a


def test_team_endpoint_interdit_au_cabinet(client: TestClient) -> None:
    """Un consultant (Cas 2) n'a pas accès au /team — endpoint réservé Cas 1."""
    data = signup_cabinet(client, email="c@cab.dz", nom="Cab")
    resp = client.get("/team", headers=auth_header(data["access_token"]))
    # 403 : le rôle consultant n'est pas patron
    assert resp.status_code == 403


def test_team_invite_interdit_au_validateur(client: TestClient) -> None:
    """Seul le patron peut inviter. Un validateur reçoit 403."""
    a = signup_entreprise(client, email="patron@x.dz", nom="X")
    client.post(
        "/team/invite",
        headers=auth_header(a["access_token"]),
        json={
            "email": "valid@x.dz",
            "username": "vv",
            "password": "motdepasse123",
            "role": "validateur",
        },
    ).raise_for_status()

    # Login du validateur
    valid_login = client.post(
        "/auth/login", json={"email": "valid@x.dz", "password": "motdepasse123"}
    ).json()

    resp = client.post(
        "/team/invite",
        headers=auth_header(valid_login["access_token"]),
        json={
            "email": "autre@x.dz",
            "username": "aa",
            "password": "motdepasse123",
            "role": "lecteur",
        },
    )
    assert resp.status_code == 403


def test_entreprise_active_header_invalide_renvoie_404(client: TestClient) -> None:
    """G2 — Cas 2, un cabinet qui pointe vers un entreprise_id inexistant/hors portefeuille → 404."""
    cab = signup_cabinet(client, email="cab1@x.dz", nom="Cab1")
    headers = {
        **auth_header(cab["access_token"]),
        "X-Entreprise-Active-Id": "99999",  # n'existe pas
    }
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 404


def test_cross_cabinet_ne_se_voient_pas(client: TestClient) -> None:
    """G2 — Deux cabinets indépendants n'accèdent pas l'un à l'autre."""
    c1 = signup_cabinet(client, email="c1@x.dz", nom="Cab1")
    c2 = signup_cabinet(client, email="c2@x.dz", nom="Cab2")

    # Chacun voit son propre contexte
    me1 = client.get("/auth/me", headers=auth_header(c1["access_token"])).json()
    me2 = client.get("/auth/me", headers=auth_header(c2["access_token"])).json()
    assert me1["cabinet_id"] != me2["cabinet_id"]
    assert me1["organisation_id"] != me2["organisation_id"]
