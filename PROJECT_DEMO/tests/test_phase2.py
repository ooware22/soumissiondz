# -*- coding: utf-8 -*-
"""Tests Phase 2 (Lots 2+3) : coffre, refs, ao, audit, prix, templates, memoire,
formulaires + isolation cross-tenant obligatoire sur chaque endpoint metier."""
from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from tests.conftest import auth_header, signup_cabinet, signup_entreprise


# ---------- helpers ----------

def _tiny_pdf(text: str = "Document de test") -> bytes:
    """Produit un PDF valide avec du texte extractible via pypdf."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for i, line in enumerate(text.split("\n")):
        c.drawString(72, 800 - i * 20, line)
    c.showPage()
    c.save()
    return buf.getvalue()


def _two_orgs(client: TestClient) -> tuple[dict, dict]:
    a = signup_entreprise(client, email="a@alpha.dz", nom="Alpha BTPH")
    b = signup_entreprise(client, email="b@bravo.dz", nom="Bravo BTPH")
    return a, b


# =========================================================================
# COFFRE
# =========================================================================

def test_coffre_types_catalogue_public(client):
    resp = client.get("/coffre/types")
    assert resp.status_code == 200
    types = resp.json()
    assert len(types) == 15
    codes = {t["code"] for t in types}
    assert {"CNAS", "CASNOS", "CACOBATPH", "NIF", "NIS", "RC"}.issubset(codes)


def test_coffre_upload_pdf_puis_list(client):
    a = signup_entreprise(client, email="u@x.dz", nom="Up")
    h = auth_header(a["access_token"])
    resp = client.post(
        "/coffre/documents",
        headers=h,
        data={"type_code": "CNAS", "date_expiration": "2027-12-31"},
        files={"file": ("cnas.pdf", _tiny_pdf("CNAS 2026"), "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    doc = resp.json()
    assert doc["type_code"] == "CNAS"
    assert doc["size_bytes"] > 0

    listing = client.get("/coffre/documents", headers=h).json()
    assert len(listing) == 1


def test_coffre_upload_type_inconnu_422(client):
    a = signup_entreprise(client, email="bad@x.dz", nom="Bad")
    resp = client.post(
        "/coffre/documents",
        headers=auth_header(a["access_token"]),
        data={"type_code": "INVENTED"},
        files={"file": ("x.pdf", _tiny_pdf(), "application/pdf")},
    )
    assert resp.status_code == 422


def test_coffre_upload_non_pdf_422(client):
    a = signup_entreprise(client, email="np@x.dz", nom="Np")
    resp = client.post(
        "/coffre/documents",
        headers=auth_header(a["access_token"]),
        data={"type_code": "NIF"},
        files={"file": ("x.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 422


def test_coffre_download_document(client):
    a = signup_entreprise(client, email="dl@x.dz", nom="Dl")
    h = auth_header(a["access_token"])
    pdf = _tiny_pdf("Attestation NIF")
    doc = client.post(
        "/coffre/documents",
        headers=h,
        data={"type_code": "NIF"},
        files={"file": ("nif.pdf", pdf, "application/pdf")},
    ).json()
    resp = client.get(f"/coffre/documents/{doc['id']}/download", headers=h)
    assert resp.status_code == 200
    assert resp.content == pdf


def test_coffre_isolation_autre_entreprise_404(client):
    """G2 : doc cree par A, acces depuis B -> 404."""
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])

    doc = client.post(
        "/coffre/documents", headers=ha,
        data={"type_code": "RC"},
        files={"file": ("rc.pdf", _tiny_pdf(), "application/pdf")},
    ).json()

    # B tente GET, download, DELETE, PATCH
    assert client.get(f"/coffre/documents/{doc['id']}", headers=hb).status_code == 404
    assert client.get(f"/coffre/documents/{doc['id']}/download", headers=hb).status_code == 404
    assert client.delete(f"/coffre/documents/{doc['id']}", headers=hb).status_code == 404
    assert client.patch(
        f"/coffre/documents/{doc['id']}", headers=hb,
        json={"commentaire": "hack"},
    ).status_code == 404

    # Le doc est toujours intact cote A
    d2 = client.get(f"/coffre/documents/{doc['id']}", headers=ha).json()
    assert d2["commentaire"] is None


def test_coffre_alertes_expiration(client):
    from datetime import date, timedelta
    a = signup_entreprise(client, email="al@x.dz", nom="Al")
    h = auth_header(a["access_token"])

    today = date.today()
    # Un doc expire dans 5j (seuil 7j), un dans 20j (seuil 30j), un dans 60j (ignore)
    for days, code in [(5, "CNAS"), (20, "CASNOS"), (60, "NIF"), (-3, "RC")]:
        exp = (today + timedelta(days=days)).isoformat()
        client.post(
            "/coffre/documents", headers=h,
            data={"type_code": code, "date_expiration": exp},
            files={"file": (f"{code}.pdf", _tiny_pdf(), "application/pdf")},
        ).raise_for_status()

    alertes = client.get("/coffre/alertes", headers=h).json()
    seuils = {a["seuil"] for a in alertes}
    # On attend 3 alertes : expire, 7j, 30j (le 60j n'est pas dans la fenetre)
    assert "expire" in seuils
    assert "7j" in seuils
    assert "30j" in seuils
    assert len(alertes) == 3


def test_coffre_delete(client):
    a = signup_entreprise(client, email="del@x.dz", nom="Del")
    h = auth_header(a["access_token"])
    doc = client.post(
        "/coffre/documents", headers=h,
        data={"type_code": "STATUTS"},
        files={"file": ("s.pdf", _tiny_pdf(), "application/pdf")},
    ).json()
    resp = client.delete(f"/coffre/documents/{doc['id']}", headers=h)
    assert resp.status_code == 200
    assert client.get(f"/coffre/documents/{doc['id']}", headers=h).status_code == 404


# =========================================================================
# REFERENCES
# =========================================================================

def test_references_crud(client):
    a = signup_entreprise(client, email="ref@x.dz", nom="Ref")
    h = auth_header(a["access_token"])
    payload = {
        "objet": "Construction ecole primaire 6 classes",
        "maitre_ouvrage": "APC Bouira",
        "montant_da": 45_000_000,
        "annee": 2023,
        "type_travaux": "batiment_public",
    }
    r = client.post("/references", headers=h, json=payload).json()
    assert r["objet"].startswith("Construction")

    # update
    client.put(f"/references/{r['id']}", headers=h, json={**payload, "annee": 2024}).raise_for_status()
    got = client.get(f"/references/{r['id']}", headers=h).json()
    assert got["annee"] == 2024

    # list
    lst = client.get("/references", headers=h).json()
    assert len(lst) == 1

    # delete
    assert client.delete(f"/references/{r['id']}", headers=h).status_code == 200
    assert client.get(f"/references/{r['id']}", headers=h).status_code == 404


def test_references_isolation_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    r = client.post("/references", headers=ha, json={
        "objet": "Travaux VRD lotissement",
        "annee": 2023,
    }).json()

    assert client.get(f"/references/{r['id']}", headers=hb).status_code == 404
    assert client.put(f"/references/{r['id']}", headers=hb, json={"objet": "hack"}).status_code == 404
    assert client.delete(f"/references/{r['id']}", headers=hb).status_code == 404


# =========================================================================
# AO + IMPORT PDF + AUDIT
# =========================================================================

def test_ao_crud(client):
    a = signup_entreprise(client, email="ao@x.dz", nom="Ao")
    h = auth_header(a["access_token"])
    ao = client.post("/ao", headers=h, json={
        "reference": "AO-2026/001",
        "objet": "Travaux de refection de voirie RN1",
        "wilaya_code": "16",
        "budget_estime_da": 25_000_000,
        "qualification_requise_cat": "III",
    }).json()
    assert ao["reference"] == "AO-2026/001"
    got = client.get(f"/ao/{ao['id']}", headers=h).json()
    assert got["id"] == ao["id"]


def test_ao_import_pdf_extrait_des_champs(client):
    a = signup_entreprise(client, email="imp@x.dz", nom="Imp")
    h = auth_header(a["access_token"])

    pdf_text = (
        "Republique Algerienne Democratique et Populaire\n"
        "Wilaya de Setif\n"
        "Appel d'offres national ouvert\n"
        "Reference : AO-2026/042\n"
        "Objet : Realisation de travaux de voirie urbaine a Setif\n"
        "Maitre d'ouvrage : APC de Setif\n"
        "Date limite de depot : 15/05/2026\n"
        "Montant estime : 35 000 000 DA\n"
        "Qualification categorie IV en travaux publics\n"
    )
    resp = client.post(
        "/ao/import-pdf", headers=h,
        files={"file": ("ao.pdf", _tiny_pdf(pdf_text), "application/pdf")},
    )
    assert resp.status_code == 201, resp.text
    out = resp.json()
    ao = out["ao"]
    # Au moins la reference et le wilaya (Setif=19) doivent sortir
    assert "reference" in out["champs_extraits"] or "wilaya_code" in out["champs_extraits"]
    assert ao["objet"]


def test_ao_isolation_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    ao = client.post("/ao", headers=ha, json={
        "objet": "Reseau AEP", "wilaya_code": "16",
    }).json()
    assert client.get(f"/ao/{ao['id']}", headers=hb).status_code == 404
    assert client.delete(f"/ao/{ao['id']}", headers=hb).status_code == 404


def test_ao_audit_25_regles(client):
    a = signup_entreprise(client, email="au@x.dz", nom="Au")
    h = auth_header(a["access_token"])
    ao = client.post("/ao", headers=h, json={
        "objet": "Construction ecole",
        "qualification_requise_cat": "III",
        "wilaya_code": "16",
        "budget_estime_da": 20_000_000,
        "qualification_requise_activites": "batiment public",
    }).json()

    audit = client.get(f"/ao/{ao['id']}/audit", headers=h).json()
    # Le moteur doit renvoyer exactement 25 regles
    assert len(audit["regles"]) == 25
    assert 0 <= audit["score"] <= 100
    assert audit["verdict_global"] in {"excellent", "bon", "insuffisant", "critique", "non_conforme"}
    # Verdicts cumulables
    assert audit["total_ok"] + audit["total_warning"] + audit["total_danger"] == 25


def test_ao_audit_isolation_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    ao = client.post("/ao", headers=ha, json={"objet": "Mon AO prive"}).json()
    assert client.get(f"/ao/{ao['id']}/audit", headers=hb).status_code == 404


# =========================================================================
# PRIX
# =========================================================================

def test_prix_catalogue_35_articles(client):
    a = signup_entreprise(client, email="pr@x.dz", nom="Pr")
    h = auth_header(a["access_token"])
    resp = client.get("/prix/articles", headers=h)
    assert resp.status_code == 200
    arts = resp.json()
    assert len(arts) == 35
    cats = {a["categorie"] for a in arts}
    # 8 categories BTPH
    assert {"terrassement", "gros_oeuvre", "vrd", "electricite",
            "plomberie", "menuiserie", "peinture", "etancheite"}.issubset(cats)


def test_prix_simulation(client):
    a = signup_entreprise(client, email="sim@x.dz", nom="Sim")
    h = auth_header(a["access_token"])
    # prime catalog
    client.get("/prix/articles", headers=h).raise_for_status()

    resp = client.post("/prix/simuler", headers=h, json={
        "postes": [
            {"article_code": "GRO002", "quantite": 100, "prix_propose_da": 29000},
            {"article_code": "VRD005", "quantite": 50, "prix_propose_da": 18000},
        ]
    })
    assert resp.status_code == 200, resp.text
    out = resp.json()
    assert len(out["postes"]) == 2
    assert all(p["verdict"] in {"bas", "ok", "haut", "hors_fourchette"} for p in out["postes"])
    assert out["montant_total_propose_da"] > 0


def test_prix_simulation_article_inconnu_422(client):
    a = signup_entreprise(client, email="zz@x.dz", nom="Zz")
    h = auth_header(a["access_token"])
    client.get("/prix/articles", headers=h).raise_for_status()
    resp = client.post("/prix/simuler", headers=h, json={
        "postes": [{"article_code": "NOPE", "quantite": 1, "prix_propose_da": 100}]
    })
    assert resp.status_code == 422


# =========================================================================
# TEMPLATES
# =========================================================================

def test_templates_liste_5(client):
    a = signup_entreprise(client, email="tp@x.dz", nom="Tp")
    resp = client.get("/templates", headers=auth_header(a["access_token"]))
    assert resp.status_code == 200
    codes = {t["code"] for t in resp.json()}
    assert codes == {"ROUTES", "BATIMENT_PUBLIC", "VRD", "LPP", "HYDRAULIQUE"}


def test_templates_chiffrage_proportionnel(client):
    a = signup_entreprise(client, email="ch@x.dz", nom="Ch")
    h = auth_header(a["access_token"])
    client.get("/prix/articles", headers=h).raise_for_status()

    resp = client.post("/templates/ROUTES/chiffrer", headers=h,
                       json={"budget_cible_da": 90_000_000})
    assert resp.status_code == 200, resp.text
    out = resp.json()
    assert out["code"] == "ROUTES"
    assert out["budget_cible_da"] == 90_000_000
    assert len(out["postes"]) >= 4
    assert out["montant_calcule_da"] > 0


def test_templates_chiffrage_code_inconnu_404(client):
    a = signup_entreprise(client, email="uk@x.dz", nom="Uk")
    resp = client.post(
        "/templates/INCONNU/chiffrer",
        headers=auth_header(a["access_token"]),
        json={"budget_cible_da": 1_000_000},
    )
    assert resp.status_code == 404


# =========================================================================
# MEMOIRE + FORMULAIRES
# =========================================================================

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_memoire_genere_docx(client):
    a = signup_entreprise(client, email="mem@x.dz", nom="Mem")
    h = auth_header(a["access_token"])
    ao = client.post("/ao", headers=h, json={"objet": "Construction stade omnisport"}).json()
    resp = client.get(f"/memoire/generer?ao_id={ao['id']}", headers=h)
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(DOCX_MIME)
    # DOCX = ZIP -> signature PK\x03\x04
    assert resp.content[:2] == b"PK"


def test_formulaire_3_types(client):
    a = signup_entreprise(client, email="fm@x.dz", nom="Fm")
    h = auth_header(a["access_token"])
    ao = client.post("/ao", headers=h, json={"objet": "AO formulaires"}).json()
    for code in ("declaration_probite", "lettre_soumission", "declaration_a_souscrire"):
        r = client.get(f"/formulaires/{code}/generer?ao_id={ao['id']}", headers=h)
        assert r.status_code == 200, f"{code}: {r.text}"
        assert r.content[:2] == b"PK"


def test_formulaire_code_inconnu_404(client):
    a = signup_entreprise(client, email="fu@x.dz", nom="Fu")
    h = auth_header(a["access_token"])
    ao = client.post("/ao", headers=h, json={"objet": "test ao court"}).json()
    assert client.get(
        f"/formulaires/invalide/generer?ao_id={ao['id']}", headers=h
    ).status_code == 404


def test_memoire_isolation_404(client):
    a, b = _two_orgs(client)
    ha, hb = auth_header(a["access_token"]), auth_header(b["access_token"])
    ao = client.post("/ao", headers=ha, json={"objet": "Mon AO prive"}).json()
    assert client.get(f"/memoire/generer?ao_id={ao['id']}", headers=hb).status_code == 404
    assert client.get(
        f"/formulaires/declaration_probite/generer?ao_id={ao['id']}", headers=hb
    ).status_code == 404


# =========================================================================
# CAS 2 — CABINET : header X-Entreprise-Active-Id
# =========================================================================

def test_cabinet_sans_header_400(client):
    """Un cabinet doit preciser X-Entreprise-Active-Id pour scoper ses actions metier."""
    cab = signup_cabinet(client, email="cab@x.dz", nom="Cab")
    resp = client.get("/coffre/documents", headers=auth_header(cab["access_token"]))
    assert resp.status_code == 400
