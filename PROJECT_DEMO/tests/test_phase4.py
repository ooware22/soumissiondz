# -*- coding: utf-8 -*-
"""Tests Phase 4 (Lot 6 — Cas 3 assistance) : catalogue, mission, mandat,
livraison, validation, contestation, journal, messagerie + isolation."""
from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import auth_header, signup_entreprise


def _create_admin_and_assistant(client: TestClient) -> tuple[dict, dict]:
    """Cree manuellement un user admin_plateforme + un assistant via /admin.

    L'admin n'a pas de signup public ; on l'injecte directement en DB pour
    le test, puis on l'utilise pour recruter un assistant via l'API.
    """
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models import Organisation, User
    from app.models.enums import OrgStatut, OrgType, PlanCode, UserRole
    from app.security import create_access_token, hash_password

    db = SessionLocal()
    try:
        org = Organisation(
            nom="SOUMISSION.DZ", type=OrgType.ENTREPRISE.value,
            plan=PlanCode.BUSINESS.value, statut=OrgStatut.ACTIF.value,
        )
        db.add(org)
        db.flush()
        admin_user = User(
            organisation_id=org.id, email="admin@soumission.dz",
            username="admin", password_hash=hash_password("adminpass1234"),
            role=UserRole.ADMIN_PLATEFORME.value, actif=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        admin_token = create_access_token(
            user_id=admin_user.id, organisation_id=org.id,
            role=admin_user.role, organisation_type=org.type,
        )
    finally:
        db.close()

    # L'admin recrute un assistant via l'API
    h_admin = auth_header(admin_token)
    resp = client.post("/admin/assistants", headers=h_admin, json={
        "email": "asst1@soumission.dz", "username": "asst1",
        "password": "assistpass1234",
        "specialites": ["BTPH", "fournitures"],
        "iban": "DZ59 0000 0000 0000 0000",
    })
    assert resp.status_code == 201, resp.text
    asst_data = resp.json()

    # L'assistant se connecte
    asst_login = client.post("/auth/login", json={
        "email": "asst1@soumission.dz", "password": "assistpass1234",
    }).json()
    return {"admin_token": admin_token, "data": asst_data}, asst_login


# =========================================================================
# CATALOGUE
# =========================================================================

def test_catalogue_prestations_seed_7(client):
    a = signup_entreprise(client, email="cat@x.dz", nom="Cat")
    resp = client.get("/assistance/prestations", headers=auth_header(a["access_token"]))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 7
    codes = {p["code"] for p in items}
    assert {"MAJ_COFFRE", "DOSSIER_CLE_EN_MAIN", "URGENCE_72H"}.issubset(codes)


def test_catalogue_non_authentifie_401(client):
    assert client.get("/assistance/prestations").status_code == 401


# =========================================================================
# ADMIN — recrutement assistant
# =========================================================================

def test_admin_recruter_assistant_403_pour_non_admin(client):
    a = signup_entreprise(client, email="np@x.dz", nom="NP")
    resp = client.post("/admin/assistants", headers=auth_header(a["access_token"]), json={
        "email": "x@x.dz", "username": "xx", "password": "motdepasse123",
    })
    assert resp.status_code == 403


def test_admin_recruter_puis_lister(client):
    admin_info, _asst_login = _create_admin_and_assistant(client)
    h = auth_header(admin_info["admin_token"])
    lst = client.get("/admin/assistants", headers=h).json()
    assert len(lst) == 1
    assert lst[0]["email"] == "asst1@soumission.dz"


# =========================================================================
# MISSION — cycle complet
# =========================================================================

def _setup_client_and_mission(client: TestClient) -> tuple[dict, dict, dict]:
    """Cree un assistant, un client, et fait demander une mission."""
    admin_info, asst_login = _create_admin_and_assistant(client)
    cli = signup_entreprise(client, email="cli@x.dz", nom="Client")
    h_cli = auth_header(cli["access_token"])
    mission = client.post("/missions", headers=h_cli, json={
        "prestation_code": "DOSSIER_CLE_EN_MAIN",
        "brief": "Preparation complete d'un dossier de soumission pour AO scolaire urgent.",
    }).json()
    return cli, asst_login, mission


def test_mission_demander_brouillon(client):
    cli, _asst_login, mission = _setup_client_and_mission(client)
    assert mission["statut"] == "brouillon"
    assert mission["prix_ht_da"] == 35000
    assert mission["prix_ttc_da"] == int(round(35000 * 1.19))


def test_mission_signer_mandat_affecte_assistant_et_passe_en_cours(client):
    cli, _asst_login, mission = _setup_client_and_mission(client)
    h = auth_header(cli["access_token"])
    resp = client.post(
        f"/missions/{mission['id']}/signer-mandat", headers=h,
        json={"accepte": True, "valide_jours": 7},
    )
    assert resp.status_code == 200, resp.text
    mandat = resp.json()
    assert mandat["statut"] == "signe"
    # Statut mission a jour
    m = client.get(f"/missions/{mission['id']}", headers=h).json()
    assert m["statut"] == "en_cours"
    assert m["assistant_id"] is not None


def test_mission_signer_sans_acceptation_400(client):
    cli, _asst_login, mission = _setup_client_and_mission(client)
    resp = client.post(
        f"/missions/{mission['id']}/signer-mandat",
        headers=auth_header(cli["access_token"]),
        json={"accepte": False, "valide_jours": 7},
    )
    assert resp.status_code == 400


def test_mission_cycle_livraison_validation(client):
    cli, asst_login, mission = _setup_client_and_mission(client)
    h_cli = auth_header(cli["access_token"])
    h_asst = auth_header(asst_login["access_token"])

    # Signature mandat
    client.post(
        f"/missions/{mission['id']}/signer-mandat", headers=h_cli,
        json={"accepte": True, "valide_jours": 7},
    ).raise_for_status()

    # L'assistant livre
    resp = client.post(
        f"/missions/{mission['id']}/livrer", headers=h_asst,
        json={"livrables": ["dossier_complet.zip", "memoire.docx"]},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["statut"] == "livree"

    # Client valide avec note
    resp = client.post(
        f"/missions/{mission['id']}/valider", headers=h_cli,
        json={"note": 5, "commentaire": "Excellent travail dans les delais."},
    )
    assert resp.status_code == 200
    assert resp.json()["statut"] == "validee"


def test_mission_contester(client):
    cli, asst_login, mission = _setup_client_and_mission(client)
    h_cli = auth_header(cli["access_token"])
    h_asst = auth_header(asst_login["access_token"])

    client.post(f"/missions/{mission['id']}/signer-mandat", headers=h_cli,
                json={"accepte": True, "valide_jours": 7}).raise_for_status()
    client.post(f"/missions/{mission['id']}/livrer", headers=h_asst,
                json={"livrables": ["x.docx"]}).raise_for_status()

    resp = client.post(f"/missions/{mission['id']}/contester", headers=h_cli,
                       json={"motif": "Memoire incomplet, sections 4 et 5 manquantes."})
    assert resp.status_code == 200
    assert resp.json()["statut"] == "contestee"


def test_mission_livrer_par_non_assistant_403(client):
    cli, _asst_login, mission = _setup_client_and_mission(client)
    h_cli = auth_header(cli["access_token"])
    client.post(f"/missions/{mission['id']}/signer-mandat", headers=h_cli,
                json={"accepte": True, "valide_jours": 7}).raise_for_status()

    # Le client lui-meme tente de livrer (role=patron, pas assistant)
    resp = client.post(f"/missions/{mission['id']}/livrer", headers=h_cli,
                       json={"livrables": ["fake.docx"]})
    assert resp.status_code == 403


def test_mission_isolation_cross_entreprise(client):
    """G2 — un autre client ne voit pas la mission."""
    cli, _asst, mission = _setup_client_and_mission(client)
    autre = signup_entreprise(client, email="aut@x.dz", nom="Autre")
    h_aut = auth_header(autre["access_token"])
    assert client.get(f"/missions/{mission['id']}", headers=h_aut).status_code == 404
    assert client.post(
        f"/missions/{mission['id']}/signer-mandat", headers=h_aut,
        json={"accepte": True, "valide_jours": 7},
    ).status_code == 404


# =========================================================================
# JOURNAL DU MANDAT
# =========================================================================

def test_journal_mandat_log_livraison(client):
    cli, asst_login, mission = _setup_client_and_mission(client)
    h_cli = auth_header(cli["access_token"])
    h_asst = auth_header(asst_login["access_token"])

    client.post(f"/missions/{mission['id']}/signer-mandat", headers=h_cli,
                json={"accepte": True, "valide_jours": 7}).raise_for_status()
    client.post(f"/missions/{mission['id']}/livrer", headers=h_asst,
                json={"livrables": ["doc.docx"]}).raise_for_status()

    journal = client.get(f"/missions/{mission['id']}/journal", headers=h_cli).json()
    assert len(journal) >= 1
    assert any(a["action_type"] == "livraison_mission" for a in journal)


# =========================================================================
# MESSAGERIE
# =========================================================================

def test_messages_client_assistant(client):
    cli, asst_login, mission = _setup_client_and_mission(client)
    h_cli = auth_header(cli["access_token"])
    h_asst = auth_header(asst_login["access_token"])

    client.post(f"/missions/{mission['id']}/signer-mandat", headers=h_cli,
                json={"accepte": True, "valide_jours": 7}).raise_for_status()

    # Client envoie un message
    r1 = client.post(f"/missions/{mission['id']}/messages", headers=h_cli,
                     json={"message": "Bonjour, AO joint en piece. Date limite lundi."})
    assert r1.status_code == 201, r1.text

    # Assistant repond
    r2 = client.post(f"/missions/{mission['id']}/messages", headers=h_asst,
                     json={"message": "Bien recu, je commence ce soir."})
    assert r2.status_code == 201

    # Chacun voit les 2 messages
    msgs_cli = client.get(f"/missions/{mission['id']}/messages", headers=h_cli).json()
    msgs_asst = client.get(f"/missions/{mission['id']}/messages", headers=h_asst).json()
    assert len(msgs_cli) == 2
    assert len(msgs_asst) == 2


def test_messages_isolation_cross_entreprise(client):
    cli, _asst, mission = _setup_client_and_mission(client)
    autre = signup_entreprise(client, email="aut2@x.dz", nom="Aut2")
    resp = client.get(
        f"/missions/{mission['id']}/messages", headers=auth_header(autre["access_token"])
    )
    assert resp.status_code == 404
