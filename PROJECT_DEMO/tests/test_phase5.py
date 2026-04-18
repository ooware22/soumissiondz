# -*- coding: utf-8 -*-
"""Tests Phase 5 — Lot 7 (plans/abos/factures/parrainage/hotline) + Lot 8 (loi 18-07)."""
from __future__ import annotations

import io
import json
import zipfile

from tests.conftest import auth_header, signup_cabinet, signup_entreprise


# =========================================================================
# PLANS + ABONNEMENTS + FACTURES
# =========================================================================

def test_plans_seed_6(client):
    a = signup_entreprise(client, email="pl@x.dz", nom="Pl")
    plans = client.get("/plans", headers=auth_header(a["access_token"])).json()
    assert len(plans) == 6  # 5 plans + HOTLINE
    codes = {p["code"] for p in plans}
    assert codes == {"DECOUVERTE", "ARTISAN", "PRO", "BUSINESS", "EXPERT", "HOTLINE"}


def test_souscrire_pro_mensuel_genere_facture(client):
    a = signup_entreprise(client, email="ab@x.dz", nom="Ab")
    h = auth_header(a["access_token"])

    abo = client.post("/abonnements", headers=h,
                      json={"plan_code": "PRO", "periodicite": "mensuel"}).json()
    assert abo["plan_code"] == "PRO"
    assert abo["montant_da"] == 10000
    assert abo["statut"] == "actif"

    factures = client.get("/factures", headers=h).json()
    assert len(factures) == 1
    f = factures[0]
    assert f["prix_ht_da"] == 10000
    assert f["prix_ttc_da"] == 11900  # 10000 * 1.19
    assert f["tva_pct"] == 19
    assert f["numero"].startswith("SDZ-")


def test_souscrire_decouverte_pas_de_facture(client):
    a = signup_entreprise(client, email="dc@x.dz", nom="Dc")
    h = auth_header(a["access_token"])
    client.post("/abonnements", headers=h,
                json={"plan_code": "DECOUVERTE", "periodicite": "mensuel"}).raise_for_status()
    factures = client.get("/factures", headers=h).json()
    assert factures == []


def test_facture_pdf_genere(client):
    a = signup_entreprise(client, email="pdf@x.dz", nom="Pdf")
    h = auth_header(a["access_token"])
    client.post("/abonnements", headers=h,
                json={"plan_code": "ARTISAN", "periodicite": "mensuel"}).raise_for_status()
    f = client.get("/factures", headers=h).json()[0]
    resp = client.get(f"/factures/{f['id']}/pdf", headers=h)
    assert resp.status_code == 200
    assert resp.content[:4] == b"%PDF"


def test_payer_facture_edahabia_mock(client):
    a = signup_entreprise(client, email="pa@x.dz", nom="Pa")
    h = auth_header(a["access_token"])
    client.post("/abonnements", headers=h,
                json={"plan_code": "PRO", "periodicite": "mensuel"}).raise_for_status()
    f = client.get("/factures", headers=h).json()[0]
    resp = client.post(f"/factures/{f['id']}/payer", headers=h,
                       json={"mode_paiement": "edahabia"})
    assert resp.status_code == 200
    assert resp.json()["statut"] == "payee"


def test_payer_facture_virement_attente(client):
    a = signup_entreprise(client, email="vi@x.dz", nom="Vi")
    h = auth_header(a["access_token"])
    client.post("/abonnements", headers=h,
                json={"plan_code": "BUSINESS", "periodicite": "annuel"}).raise_for_status()
    f = client.get("/factures", headers=h).json()[0]
    resp = client.post(f"/factures/{f['id']}/payer", headers=h,
                       json={"mode_paiement": "virement"})
    assert resp.json()["statut"] == "en_attente_virement"


def test_facture_isolation_404(client):
    """G2 — la facture d'A n'est pas accessible/payable depuis B."""
    a = signup_entreprise(client, email="fa@x.dz", nom="Fa")
    b = signup_entreprise(client, email="fb@x.dz", nom="Fb")
    ha = auth_header(a["access_token"])
    hb = auth_header(b["access_token"])
    client.post("/abonnements", headers=ha,
                json={"plan_code": "PRO", "periodicite": "mensuel"}).raise_for_status()
    f = client.get("/factures", headers=ha).json()[0]
    assert client.get(f"/factures/{f['id']}/pdf", headers=hb).status_code == 404
    assert client.post(
        f"/factures/{f['id']}/payer", headers=hb, json={"mode_paiement": "cib"}
    ).status_code == 404
    # B ne voit pas la facture d'A dans son listing
    assert client.get("/factures", headers=hb).json() == []


# =========================================================================
# PARRAINAGE
# =========================================================================

def test_parrainage_genere_code_unique(client):
    a = signup_entreprise(client, email="pr1@x.dz", nom="Pr1")
    h = auth_header(a["access_token"])
    code1 = client.get("/parrainage/mon-code", headers=h).json()
    assert code1["code"].startswith("SDZ-")
    # Idempotent : 2eme appel renvoie le meme code
    code2 = client.get("/parrainage/mon-code", headers=h).json()
    assert code1["code"] == code2["code"]


def test_parrainage_codes_distincts_par_user(client):
    a = signup_entreprise(client, email="u1@x.dz", nom="U1")
    b = signup_entreprise(client, email="u2@x.dz", nom="U2")
    c1 = client.get("/parrainage/mon-code", headers=auth_header(a["access_token"])).json()
    c2 = client.get("/parrainage/mon-code", headers=auth_header(b["access_token"])).json()
    assert c1["code"] != c2["code"]


def test_parrainage_commissions_vide(client):
    a = signup_entreprise(client, email="pc@x.dz", nom="Pc")
    h = auth_header(a["access_token"])
    assert client.get("/parrainage/mes-commissions", headers=h).json() == []


# =========================================================================
# HOTLINE
# =========================================================================

def test_hotline_creer_lister_ticket(client):
    a = signup_entreprise(client, email="ho@x.dz", nom="Ho")
    h = auth_header(a["access_token"])
    t = client.post("/hotline", headers=h, json={
        "niveau": "technique", "sujet": "Probleme upload PDF",
        "description": "Le PDF de 12 Mo refuse l'upload, voir capture jointe.",
    }).json()
    assert t["statut"] == "ouvert"
    assert t["niveau"] == "technique"
    lst = client.get("/hotline", headers=h).json()
    assert len(lst) == 1


def test_hotline_isolation_404(client):
    a = signup_entreprise(client, email="ha@x.dz", nom="Ha")
    b = signup_entreprise(client, email="hb@x.dz", nom="Hb")
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    client.post("/hotline", headers=ha, json={
        "niveau": "conseil", "sujet": "Question", "description": "Comment configurer l'audit ?",
    }).raise_for_status()
    # B ne voit pas le ticket d'A
    assert client.get("/hotline", headers=hb).json() == []


def test_hotline_repondre_403_si_non_admin(client):
    a = signup_entreprise(client, email="hr@x.dz", nom="Hr")
    h = auth_header(a["access_token"])
    t = client.post("/hotline", headers=h, json={
        "niveau": "expertise", "sujet": "AO complexe",
        "description": "Besoin avis sur AO multi-tranches.",
    }).json()
    resp = client.post(f"/hotline/{t['id']}/repondre", headers=h,
                       json={"reponse": "tentative client"})
    assert resp.status_code == 403


# =========================================================================
# CONFORMITE LOI 18-07
# =========================================================================

def test_confidentialite_page_publique(client):
    resp = client.get("/confidentialite")
    assert resp.status_code == 200
    body = resp.json()
    assert "loi 18-07" in body["texte"].lower()
    assert "version" in body


def test_consentement_cgu(client):
    a = signup_entreprise(client, email="cg@x.dz", nom="Cg")
    h = auth_header(a["access_token"])
    resp = client.post("/confidentialite/cgu", headers=h, json={"accepte": True})
    assert resp.status_code == 200
    assert resp.json()["user_id"] == a["user_id"]


def test_consentement_cgu_refus_400(client):
    a = signup_entreprise(client, email="cr@x.dz", nom="Cr")
    resp = client.post(
        "/confidentialite/cgu", headers=auth_header(a["access_token"]),
        json={"accepte": False},
    )
    assert resp.status_code == 400


def test_export_donnees_zip_json(client):
    a = signup_entreprise(client, email="ex@x.dz", nom="Ex")
    h = auth_header(a["access_token"])
    # Quelques donnees pour avoir du contenu
    client.post("/references", headers=h, json={
        "objet": "Test reference export", "annee": 2024,
    }).raise_for_status()

    resp = client.get("/confidentialite/export", headers=h)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"

    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    assert "export_donnees.json" in zf.namelist()
    data = json.loads(zf.read("export_donnees.json"))
    assert data["organisation"]["nom"] == "Ex"
    assert len(data["users"]) == 1
    # Hash mot de passe redacte
    assert data["users"][0]["password_hash"] == "[REDACTED]"
    assert len(data["entreprises"]) == 1
    assert len(data["references"]) == 1


def test_supprimer_compte_soft_delete(client):
    a = signup_entreprise(client, email="sd@x.dz", nom="Sd")
    h = auth_header(a["access_token"])
    resp = client.delete("/confidentialite/compte", headers=h)
    assert resp.status_code == 200
    # Le user n'est plus actif
    me = client.get("/auth/me", headers=h)
    assert me.status_code == 401  # actif=False


def test_supprimer_compte_lecteur_403(client):
    a = signup_entreprise(client, email="le@x.dz", nom="Le")
    h_patron = auth_header(a["access_token"])
    # Patron invite un lecteur
    client.post("/team/invite", headers=h_patron, json={
        "email": "lec@x.dz", "username": "lec",
        "password": "motdepasse123", "role": "lecteur",
    }).raise_for_status()
    lec = client.post("/auth/login", json={
        "email": "lec@x.dz", "password": "motdepasse123",
    }).json()
    resp = client.delete("/confidentialite/compte", headers=auth_header(lec["access_token"]))
    assert resp.status_code == 403


def test_purge_job(client):
    """Le job de purge supprime les organisations suspendues > 30 jours."""
    from datetime import date, timedelta

    from app.database import SessionLocal
    from app.models import Organisation
    from app.models.enums import OrgStatut
    from app.routers.conformite import purger_comptes_expirees

    a = signup_entreprise(client, email="pj@x.dz", nom="Pj")

    db = SessionLocal()
    try:
        # Force le statut suspendu et un updated_at vieux
        org = db.query(Organisation).filter(Organisation.nom == "Pjxx").one_or_none()
        # Le helper signup_entreprise pad le nom a 2 char min ; "Pj" reste "Pj".
        # On retombe sur la 1ere ligne par defaut.
        if org is None:
            org = db.query(Organisation).first()
        org.statut = OrgStatut.SUSPENDU.value
        # On simule un updated_at de J-31
        from datetime import datetime, timezone
        org.updated_at = datetime.now(timezone.utc) - timedelta(days=31)
        db.commit()
    finally:
        db.close()

    db = SessionLocal()
    try:
        n = purger_comptes_expirees(db, today=date.today())
        assert n >= 1
    finally:
        db.close()
