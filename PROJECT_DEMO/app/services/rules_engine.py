# -*- coding: utf-8 -*-
"""Moteur de regles — 25 regles d'audit de conformite entreprise <-> AO.

Chaque regle retourne verdict in {"ok", "warning", "danger"} et un message FR.
Score global : somme des poids des regles "ok" / somme totale des poids, sur 100.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import AppelOffres, Document, Entreprise, Reference


@dataclass
class RuleResult:
    code: str
    libelle: str
    categorie: str
    poids: int
    verdict: str  # ok | warning | danger
    message: str
    action: str | None = None


@dataclass
class AuditReport:
    score: int
    verdict_global: str
    regles: list[RuleResult]
    total_ok: int
    total_warning: int
    total_danger: int


def _get_doc(docs: list["Document"], code: str) -> "Document | None":
    return next((d for d in docs if d.type_code == code), None)


def _doc_valide(docs: list["Document"], code: str, today: date) -> tuple[str, str]:
    """Retourne (verdict, msg) pour la presence + validite d'un document."""
    d = _get_doc(docs, code)
    if d is None:
        return "danger", f"Document {code} absent du coffre-fort."
    if d.date_expiration:
        delta = (d.date_expiration - today).days
        if delta < 0:
            return "danger", f"Document {code} expire depuis {-delta} jours."
        if delta <= 7:
            return "warning", f"Document {code} expire dans {delta} jours — renouveler urgence."
        if delta <= 30:
            return "warning", f"Document {code} expire dans {delta} jours."
    return "ok", f"Document {code} present et valide."


def run_audit(
    entreprise: "Entreprise",
    ao: "AppelOffres",
    docs: list["Document"],
    references: list["Reference"],
    today: date | None = None,
) -> AuditReport:
    today = today or date.today()
    results: list[RuleResult] = []

    # ----- Categorie : DOCUMENTS OFFICIELS (10 regles, poids 5 chacune) -----
    for code in ["CNAS", "CASNOS", "CACOBATPH", "NIF", "NIS", "RC",
                 "EXTRAIT_ROLE", "ATTESTATION_FISCALE", "STATUTS", "CASIER_JUDICIAIRE"]:
        verdict, msg = _doc_valide(docs, code, today)
        results.append(RuleResult(
            code=f"DOC_{code}", libelle=f"Document {code}", categorie="documents",
            poids=5, verdict=verdict, message=msg,
            action=f"Uploader ou renouveler le document {code}" if verdict != "ok" else None,
        ))

    # ----- BILANS (3 regles) -----
    for an in ["2022", "2023", "2024"]:
        d = _get_doc(docs, f"BILAN_{an}")
        verdict = "ok" if d else "warning"
        results.append(RuleResult(
            code=f"BILAN_{an}", libelle=f"Bilan financier {an}", categorie="finance",
            poids=3, verdict=verdict,
            message=(f"Bilan {an} present." if d else f"Bilan {an} manquant."),
            action=None if d else f"Importer le bilan {an}",
        ))

    # ----- QUALIFICATION BTPH (1 regle poids 8) -----
    if ao.qualification_requise_cat:
        if entreprise.qualification_cat is None:
            results.append(RuleResult(
                code="QUAL_CAT", libelle="Categorie de qualification BTPH",
                categorie="qualification", poids=8, verdict="danger",
                message=f"AO exige categorie {ao.qualification_requise_cat}, entreprise sans qualification.",
                action="Saisir la categorie de qualification de l'entreprise.",
            ))
        else:
            # Compare numerique romaine grossiere (I<II<III<IV<V<VI<VII<VIII<IX)
            roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
            req = roman.index(ao.qualification_requise_cat) if ao.qualification_requise_cat in roman else -1
            has = roman.index(entreprise.qualification_cat) if entreprise.qualification_cat in roman else -1
            if has >= req and has >= 0:
                results.append(RuleResult(
                    code="QUAL_CAT", libelle="Categorie qualification",
                    categorie="qualification", poids=8, verdict="ok",
                    message=f"Qualification entreprise ({entreprise.qualification_cat}) >= requise ({ao.qualification_requise_cat}).",
                ))
            else:
                results.append(RuleResult(
                    code="QUAL_CAT", libelle="Categorie qualification",
                    categorie="qualification", poids=8, verdict="danger",
                    message=f"Qualification entreprise ({entreprise.qualification_cat}) < requise ({ao.qualification_requise_cat}).",
                    action="Monter en qualification ou renoncer a cet AO.",
                ))
    else:
        results.append(RuleResult(
            code="QUAL_CAT", libelle="Categorie qualification",
            categorie="qualification", poids=8, verdict="ok",
            message="Aucune qualification particuliere exigee par l'AO.",
        ))

    # QUAL_EXPIRATION (1 regle poids 5)
    if entreprise.qualification_expiration:
        delta = (entreprise.qualification_expiration - today).days
        if delta < 0:
            results.append(RuleResult(
                code="QUAL_EXPIR", libelle="Expiration qualification",
                categorie="qualification", poids=5, verdict="danger",
                message=f"Qualification expiree depuis {-delta} jours.",
                action="Renouveler le certificat de qualification.",
            ))
        elif delta <= 30:
            results.append(RuleResult(
                code="QUAL_EXPIR", libelle="Expiration qualification",
                categorie="qualification", poids=5, verdict="warning",
                message=f"Qualification expire dans {delta} jours.",
                action="Renouveler le certificat de qualification.",
            ))
        else:
            results.append(RuleResult(
                code="QUAL_EXPIR", libelle="Expiration qualification",
                categorie="qualification", poids=5, verdict="ok",
                message=f"Qualification valide ({delta} jours restants).",
            ))
    else:
        results.append(RuleResult(
            code="QUAL_EXPIR", libelle="Expiration qualification",
            categorie="qualification", poids=5, verdict="warning",
            message="Date d'expiration de la qualification non renseignee.",
        ))

    # ----- DELAI AO (1 regle poids 6) -----
    if ao.date_limite:
        delta = (ao.date_limite - today).days
        if delta < 0:
            verdict, msg = "danger", f"Date limite depassee depuis {-delta} jours."
        elif delta < 3:
            verdict, msg = "danger", f"Date limite dans {delta} jours — delai extremement tendu."
        elif delta < 7:
            verdict, msg = "warning", f"Date limite dans {delta} jours — preparation urgente."
        else:
            verdict, msg = "ok", f"Date limite dans {delta} jours — delai confortable."
        results.append(RuleResult(
            code="AO_DELAI", libelle="Delai jusqu'a date limite",
            categorie="planning", poids=6, verdict=verdict, message=msg,
        ))
    else:
        results.append(RuleResult(
            code="AO_DELAI", libelle="Delai jusqu'a date limite",
            categorie="planning", poids=6, verdict="warning",
            message="Date limite non renseignee dans l'AO.",
        ))

    # ----- REFERENCES (3 regles poids 4 chacune) -----
    n_refs = len(references)
    results.append(RuleResult(
        code="REF_COUNT", libelle="Nombre de references",
        categorie="experience", poids=4,
        verdict=("ok" if n_refs >= 3 else "warning" if n_refs >= 1 else "danger"),
        message=f"{n_refs} reference(s) declaree(s).",
        action="Ajouter des references de marches executes." if n_refs < 3 else None,
    ))

    # Reference du meme type que l'AO
    if ao.qualification_requise_activites:
        activites = ao.qualification_requise_activites.lower()
        match = any(r.type_travaux and r.type_travaux.lower() in activites for r in references)
        results.append(RuleResult(
            code="REF_TYPE", libelle="Reference de type correspondant",
            categorie="experience", poids=4,
            verdict=("ok" if match else "warning"),
            message=("Au moins une reference du type requis." if match else
                    "Aucune reference ne correspond au type de travaux demande."),
        ))
    else:
        results.append(RuleResult(
            code="REF_TYPE", libelle="Reference de type correspondant",
            categorie="experience", poids=4, verdict="ok",
            message="Type de travaux AO non precise — regle non applicable.",
        ))

    # Reference recente (< 5 ans)
    if n_refs > 0:
        annee_limite = today.year - 5
        recent = any((r.annee or 0) >= annee_limite for r in references)
        results.append(RuleResult(
            code="REF_RECENT", libelle="Reference de moins de 5 ans",
            categorie="experience", poids=4,
            verdict=("ok" if recent else "warning"),
            message=("Au moins une reference recente." if recent else
                    "Toutes les references ont plus de 5 ans."),
        ))
    else:
        results.append(RuleResult(
            code="REF_RECENT", libelle="Reference recente",
            categorie="experience", poids=4, verdict="danger",
            message="Aucune reference disponible.",
        ))

    # ----- COHERENCE WILAYA (1 regle poids 3) -----
    if ao.wilaya_code and entreprise.wilaya_code:
        same = ao.wilaya_code == entreprise.wilaya_code
        results.append(RuleResult(
            code="GEO_WILAYA", libelle="Coherence wilaya",
            categorie="geographie", poids=3,
            verdict=("ok" if same else "warning"),
            message=("Meme wilaya que l'AO." if same else
                    f"AO en wilaya {ao.wilaya_code}, entreprise en {entreprise.wilaya_code} — verifier logistique."),
        ))
    else:
        results.append(RuleResult(
            code="GEO_WILAYA", libelle="Coherence wilaya",
            categorie="geographie", poids=3, verdict="warning",
            message="Wilaya non precisee cote AO ou entreprise.",
        ))

    # ----- CAPACITE FINANCIERE (2 regles) -----
    if ao.budget_estime_da and entreprise.ca_moyen_da:
        ratio = ao.budget_estime_da / max(entreprise.ca_moyen_da, 1)
        if ratio <= 0.3:
            verdict, msg = "ok", f"Budget AO = {ratio:.0%} du CA moyen — largement supporte."
        elif ratio <= 0.7:
            verdict, msg = "ok", f"Budget AO = {ratio:.0%} du CA moyen — supportable."
        elif ratio <= 1.5:
            verdict, msg = "warning", f"Budget AO = {ratio:.0%} du CA moyen — trace serree."
        else:
            verdict, msg = "danger", f"Budget AO = {ratio:.0%} du CA moyen — probablement hors capacite."
        results.append(RuleResult(
            code="FIN_RATIO", libelle="Ratio budget AO / CA moyen",
            categorie="finance", poids=5, verdict=verdict, message=msg,
        ))
    else:
        results.append(RuleResult(
            code="FIN_RATIO", libelle="Ratio budget / CA",
            categorie="finance", poids=5, verdict="warning",
            message="Budget AO ou CA entreprise non renseigne.",
        ))

    # Attestation bancaire presente
    results.append(RuleResult(
        code="DOC_ATTEST_BANK", libelle="Attestation bancaire",
        categorie="finance", poids=3,
        verdict=("ok" if _get_doc(docs, "ATTESTATION_BANCAIRE") else "warning"),
        message=("Attestation bancaire presente." if _get_doc(docs, "ATTESTATION_BANCAIRE") else
                "Attestation bancaire manquante — souvent exigee pour la soumission."),
        action=None if _get_doc(docs, "ATTESTATION_BANCAIRE") else "Demander une attestation bancaire",
    ))

    # ----- IDENTITE (3 regles poids 2) -----
    results.append(RuleResult(
        code="ID_NIF", libelle="NIF entreprise",
        categorie="identite", poids=2,
        verdict=("ok" if entreprise.nif else "warning"),
        message=("NIF renseigne." if entreprise.nif else "NIF de l'entreprise non renseigne."),
    ))
    results.append(RuleResult(
        code="ID_RC", libelle="RC entreprise",
        categorie="identite", poids=2,
        verdict=("ok" if entreprise.rc else "warning"),
        message=("RC renseigne." if entreprise.rc else "RC de l'entreprise non renseigne."),
    ))
    results.append(RuleResult(
        code="ID_GERANT", libelle="Gerant entreprise",
        categorie="identite", poids=2,
        verdict=("ok" if entreprise.gerant else "warning"),
        message=("Gerant renseigne." if entreprise.gerant else "Nom du gerant non renseigne."),
    ))

    # Calcul score global
    total_poids = sum(r.poids for r in results)
    poids_ok = sum(r.poids for r in results if r.verdict == "ok")
    poids_warn = sum(r.poids for r in results if r.verdict == "warning")
    score = int(round(100 * (poids_ok + poids_warn * 0.5) / max(total_poids, 1)))

    n_danger = sum(1 for r in results if r.verdict == "danger")
    n_warn = sum(1 for r in results if r.verdict == "warning")
    n_ok = sum(1 for r in results if r.verdict == "ok")

    if n_danger > 0:
        verdict_global = "non_conforme"
    elif score >= 85:
        verdict_global = "excellent"
    elif score >= 70:
        verdict_global = "bon"
    elif score >= 50:
        verdict_global = "insuffisant"
    else:
        verdict_global = "critique"

    return AuditReport(
        score=score,
        verdict_global=verdict_global,
        regles=results,
        total_ok=n_ok,
        total_warning=n_warn,
        total_danger=n_danger,
    )
