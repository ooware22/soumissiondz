# -*- coding: utf-8 -*-
"""Tests Phase 3 (Lots 4+5) : dossiers/kanban/workflow, cautions, soumissions,
cabinet portefeuille + comparateur. Isolation cross-tenant obligatoire."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

from tests.conftest import auth_header, signup_cabinet, signup_entreprise


def _two_orgs(client):
    a = signup_entreprise(client, email="a@al.dz", nom="Alpha")
    b = signup_entreprise(client, email="b@br.dz", nom="Bravo")
    return a, b


# =========================================================================
# DOSSIERS / KANBAN / WORKFLOW
# =========================================================================

def test_dossier_crud(client):
    a = signup_entreprise(client, email="d@x.dz", nom="Dx")
    h = auth_header(a["access_token"])
    d = client.post("/dossiers", headers=h, json={
        "nom": "Dossier ecole primaire Bouira",
        "date_cible": "2026-09-30",
    }).json()
    assert d["statut"] == "a_faire"
    assert d["etape_actuelle"] == "profil"

    got = client.get(f"/dossiers/{d['id']}", headers=h).json()
    assert got["nom"] == d["nom"]


def test_dossier_avancer_etapes(client):
    a = signup_entreprise(client, email="av@x.dz", nom="Av")
    h = auth_header(a["access_token"])
    d = client.post("/dossiers", headers=h, json={"nom": "Test avancer"}).json()

    etapes = ["documents", "audit", "chiffrage", "memoire", "verification", "depot"]
    for e in etapes:
        d = client.post(f"/dossiers/{d['id']}/avancer", headers=h).json()
        assert d["etape_actuelle"] == e

    # Au-dela : 409
    resp = client.post(f"/dossiers/{d['id']}/avancer", headers=h)
    assert resp.status_code == 409


def test_kanban_4_colonnes(client):
    a = signup_entreprise(client, email="kb@x.dz", nom="Kb")
    h = auth_header(a["access_token"])
    client.post("/dossiers", headers=h, json={"nom": "Doss 1"}).raise_for_status()
    d2 = client.post("/dossiers", headers=h, json={"nom": "Doss 2"}).json()
    client.patch(f"/dossiers/{d2['id']}", headers=h,
                 json={"statut": "en_cours"}).raise_for_status()

    kb = client.get("/dossiers/kanban", headers=h).json()
    assert len(kb["colonnes"]) == 4
    statuts = [c["statut"] for c in kb["colonnes"]]
    assert statuts == ["a_faire", "en_cours", "a_valider", "termine"]
    a_faire_count = sum(len(c["dossiers"]) for c in kb["colonnes"] if c["statut"] == "a_faire")
    en_cours_count = sum(len(c["dossiers"]) for c in kb["colonnes"] if c["statut"] == "en_cours")
    assert a_faire_count == 1
    assert en_cours_count == 1


def test_workflow_3_niveaux(client):
    """Patron cree un dossier, le passe en cours, prepa le valide -> a_valider,
    patron le valide -> termine."""
    a = signup_entreprise(client, email="wf@x.dz", nom="Wf")
    h_patron = auth_header(a["access_token"])

    # Patron invite un preparateur et un validateur
    client.post("/team/invite", headers=h_patron, json={
        "email": "prep@wf.dz", "username": "pp", "password": "motdepasse123", "role": "preparateur",
    }).raise_for_status()
    client.post("/team/invite", headers=h_patron, json={
        "email": "val@wf.dz", "username": "vv", "password": "motdepasse123", "role": "validateur",
    }).raise_for_status()
    h_prep = auth_header(client.post("/auth/login", json={
        "email": "prep@wf.dz", "password": "motdepasse123",
    }).json()["access_token"])
    h_val = auth_header(client.post("/auth/login", json={
        "email": "val@wf.dz", "password": "motdepasse123",
    }).json()["access_token"])

    d = client.post("/dossiers", headers=h_patron, json={"nom": "Workflow test"}).json()

    # Patron passe en_cours
    client.patch(f"/dossiers/{d['id']}", headers=h_patron,
                 json={"statut": "en_cours"}).raise_for_status()

    # Preparateur valide -> a_valider
    out = client.post(f"/dossiers/{d['id']}/valider", headers=h_prep).json()
    assert out["statut"] == "a_valider"

    # Validateur intermediaire (pas de changement)
    out = client.post(f"/dossiers/{d['id']}/valider", headers=h_val).json()
    assert out["statut"] == "a_valider"

    # Patron tranche -> termine
    out = client.post(f"/dossiers/{d['id']}/valider", headers=h_patron).json()
    assert out["statut"] == "termine"


def test_dossier_isolation_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    d = client.post("/dossiers", headers=ha, json={"nom": "Prive A"}).json()

    assert client.get(f"/dossiers/{d['id']}", headers=hb).status_code == 404
    assert client.patch(f"/dossiers/{d['id']}", headers=hb,
                        json={"nom": "hack"}).status_code == 404
    assert client.post(f"/dossiers/{d['id']}/avancer", headers=hb).status_code == 404
    assert client.post(f"/dossiers/{d['id']}/valider", headers=hb).status_code == 404
    assert client.delete(f"/dossiers/{d['id']}", headers=hb).status_code == 404


def test_dossier_avec_ao_autre_entreprise_404(client):
    """Cas tordu : dossier qui pointerait sur un AO d'une autre entreprise."""
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    ao_b = client.post("/ao", headers=hb, json={"objet": "AO de B"}).json()
    # A tente de creer un dossier qui pointe vers l'AO de B
    resp = client.post("/dossiers", headers=ha,
                       json={"nom": "Hack", "ao_id": ao_b["id"]})
    assert resp.status_code == 404


# =========================================================================
# CAUTIONS
# =========================================================================

def test_caution_crud_et_resume(client):
    a = signup_entreprise(client, email="cau@x.dz", nom="Cau")
    h = auth_header(a["access_token"])
    today = date.today()

    c1 = client.post("/cautions", headers=h, json={
        "type_code": "caution_soumission",
        "montant_da": 250_000,
        "banque": "BNA",
        "date_emission": today.isoformat(),
        "date_recuperation_estimee": (today + timedelta(days=10)).isoformat(),
    }).json()
    c2 = client.post("/cautions", headers=h, json={
        "type_code": "garantie_bonne_execution",
        "montant_da": 1_500_000,
        "date_recuperation_estimee": (today + timedelta(days=60)).isoformat(),
    }).json()

    resume = client.get("/cautions/resume", headers=h).json()
    assert resume["total_bloque_da"] == 1_750_000
    assert resume["nombre_actives"] == 2
    assert resume["par_type"]["caution_soumission"] == 250_000
    # 1 alerte 15j (cau soumission a 10j), 0 alerte au-dela 30j
    assert len(resume["alertes"]) == 1
    assert resume["alertes"][0]["seuil"] == "15j"


def test_caution_recuperer_change_statut(client):
    a = signup_entreprise(client, email="rec@x.dz", nom="Rec")
    h = auth_header(a["access_token"])
    c = client.post("/cautions", headers=h, json={
        "type_code": "retenue_garantie", "montant_da": 100_000,
    }).json()
    out = client.post(f"/cautions/{c['id']}/recuperer", headers=h).json()
    assert out["statut"] == "recuperee"

    resume = client.get("/cautions/resume", headers=h).json()
    # recuperee -> n'apparait plus dans le total
    assert resume["nombre_actives"] == 0
    assert resume["total_bloque_da"] == 0


def test_caution_type_invalide_422(client):
    a = signup_entreprise(client, email="tc@x.dz", nom="Tc")
    h = auth_header(a["access_token"])
    resp = client.post("/cautions", headers=h, json={
        "type_code": "BIDON", "montant_da": 100,
    })
    assert resp.status_code == 422


def test_caution_isolation_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    c = client.post("/cautions", headers=ha, json={
        "type_code": "caution_soumission", "montant_da": 50000,
    }).json()
    assert client.get(f"/cautions/{c['id']}", headers=hb).status_code == 404
    assert client.put(f"/cautions/{c['id']}", headers=hb,
                      json={"type_code": "caution_soumission", "montant_da": 1}).status_code == 404
    assert client.post(f"/cautions/{c['id']}/recuperer", headers=hb).status_code == 404
    assert client.delete(f"/cautions/{c['id']}", headers=hb).status_code == 404
    # Le resume de B n'inclut pas la caution de A
    resume_b = client.get("/cautions/resume", headers=hb).json()
    assert resume_b["nombre_actives"] == 0


# =========================================================================
# SOUMISSIONS HISTORIQUE
# =========================================================================

def test_soumission_calcul_ecart(client):
    a = signup_entreprise(client, email="so@x.dz", nom="So")
    h = auth_header(a["access_token"])
    s = client.post("/soumissions", headers=h, json={
        "date_depot": "2026-03-15",
        "rang": 2,
        "montant_soumissionne_da": 22_000_000,
        "montant_attributaire_da": 20_000_000,
        "statut": "perdu",
        "raison_libre": "Concurrent moins-disant de 2M",
    }).json()
    # ecart = (22 - 20) / 20 = 10%
    assert s["ecart_pct"] == 10


def test_soumission_isolation_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    s = client.post("/soumissions", headers=ha, json={
        "statut": "gagne", "montant_soumissionne_da": 1_000_000,
    }).json()
    assert client.get(f"/soumissions/{s['id']}", headers=hb).status_code == 404
    assert client.delete(f"/soumissions/{s['id']}", headers=hb).status_code == 404


def test_soumission_avec_ao_autre_entreprise_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    ao_b = client.post("/ao", headers=hb, json={"objet": "AO B"}).json()
    resp = client.post("/soumissions", headers=ha, json={
        "ao_id": ao_b["id"], "statut": "en_cours",
    })
    assert resp.status_code == 404


# =========================================================================
# CABINET (Cas 2)
# =========================================================================

def test_cabinet_ajoute_entreprise_au_portefeuille(client):
    cab = signup_cabinet(client, email="cab@x.dz", nom="Cabinet Mourad")
    h = auth_header(cab["access_token"])
    ent = client.post("/cabinet/entreprises", headers=h, json={
        "nom": "Entreprise BTPH 1",
        "forme_juridique": "SARL",
        "wilaya_code": "16",
        "secteur": "BTPH",
    }).json()
    assert ent["nom"] == "Entreprise BTPH 1"

    # liste avec indicateurs
    portefeuille = client.get("/cabinet/entreprises", headers=h).json()
    assert len(portefeuille) == 1
    assert portefeuille[0]["nb_dossiers_en_cours"] == 0
    assert portefeuille[0]["nb_alertes_documents"] == 0


def test_cabinet_endpoint_interdit_aux_entreprises_403(client):
    """Une entreprise Cas 1 ne doit pas pouvoir appeler /cabinet/*."""
    a = signup_entreprise(client, email="e@x.dz", nom="E")
    resp = client.get("/cabinet/entreprises", headers=auth_header(a["access_token"]))
    assert resp.status_code == 403


def test_cabinet_isolation_entre_2_cabinets_404(client):
    """G2 : l'entreprise du cabinet 1 n'est pas visible par le cabinet 2."""
    cab1 = signup_cabinet(client, email="c1@x.dz", nom="Cab1")
    cab2 = signup_cabinet(client, email="c2@x.dz", nom="Cab2")
    h1 = auth_header(cab1["access_token"])
    h2 = auth_header(cab2["access_token"])

    ent = client.post("/cabinet/entreprises", headers=h1, json={"nom": "Ent du cab1"}).json()

    # Cab2 voit son portefeuille vide
    p2 = client.get("/cabinet/entreprises", headers=h2).json()
    assert p2 == []

    # Cab2 ne peut pas acceder a l'entreprise du Cab1
    assert client.get(f"/cabinet/entreprises/{ent['id']}", headers=h2).status_code == 404
    assert client.delete(f"/cabinet/entreprises/{ent['id']}", headers=h2).status_code == 404


def test_cabinet_comparer_classement_par_score(client):
    cab = signup_cabinet(client, email="cmp@x.dz", nom="Cab")
    h = auth_header(cab["access_token"])

    # Cabinet ajoute 2 entreprises
    e1 = client.post("/cabinet/entreprises", headers=h,
                     json={"nom": "Ent1", "wilaya_code": "16"}).json()
    e2 = client.post("/cabinet/entreprises", headers=h,
                     json={"nom": "Ent2", "wilaya_code": "19"}).json()

    # AO sur l'entreprise 1 (via header X-Entreprise-Active-Id)
    h_e1 = {**h, "X-Entreprise-Active-Id": str(e1["id"])}
    ao = client.post("/ao", headers=h_e1, json={
        "objet": "Construction batiment public",
        "wilaya_code": "16",
    }).json()

    # Comparer
    cmp = client.get(f"/cabinet/comparer?ao_id={ao['id']}", headers=h).json()
    assert cmp["ao_id"] == ao["id"]
    assert len(cmp["classement"]) == 2
    # Classement decroissant par score
    scores = [e["score"] for e in cmp["classement"]]
    assert scores == sorted(scores, reverse=True)


def test_cabinet_comparer_ao_hors_portefeuille_404(client):
    """G2 : un cabinet ne peut pas comparer sur un AO qui n'est pas dans son portefeuille."""
    cab1 = signup_cabinet(client, email="cc1@x.dz", nom="Cc1")
    cab2 = signup_cabinet(client, email="cc2@x.dz", nom="Cc2")
    h1 = auth_header(cab1["access_token"])
    h2 = auth_header(cab2["access_token"])

    e1 = client.post("/cabinet/entreprises", headers=h1, json={"nom": "EntCab1"}).json()
    h_e1 = {**h1, "X-Entreprise-Active-Id": str(e1["id"])}
    ao1 = client.post("/ao", headers=h_e1, json={"objet": "AO du cab1"}).json()

    # Cab2 essaie de comparer pour cet AO -> 404
    resp = client.get(f"/cabinet/comparer?ao_id={ao1['id']}", headers=h2)
    assert resp.status_code == 404
