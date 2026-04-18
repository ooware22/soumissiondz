# -*- coding: utf-8 -*-
"""Schemas Pydantic — coffre, references, AO, audit, prix, templates."""
from __future__ import annotations

from datetime import date

from pydantic import Field

from app.schemas.common import BaseSchema


# ----- Coffre -----
class DocumentTypeOut(BaseSchema):
    code: str
    libelle: str


class DocumentOut(BaseSchema):
    id: int
    type_code: str
    filename: str
    size_bytes: int
    date_emission: date | None = None
    date_expiration: date | None = None
    commentaire: str | None = None


class DocumentUpdateIn(BaseSchema):
    date_emission: date | None = None
    date_expiration: date | None = None
    commentaire: str | None = Field(default=None, max_length=2000)


class AlerteDocOut(BaseSchema):
    id: int
    type_code: str
    date_expiration: date
    jours_restants: int
    seuil: str  # "7j" | "15j" | "30j" | "expire"


# ----- References -----
class ReferenceIn(BaseSchema):
    objet: str = Field(..., min_length=3, max_length=300)
    maitre_ouvrage: str | None = Field(default=None, max_length=200)
    montant_da: int | None = Field(default=None, ge=0)
    annee: int | None = Field(default=None, ge=1990, le=2100)
    type_travaux: str | None = Field(default=None, max_length=100)


class ReferenceOut(ReferenceIn):
    id: int


# ----- Appel d'offres -----
class AoIn(BaseSchema):
    reference: str | None = Field(default=None, max_length=100)
    objet: str = Field(..., min_length=3, max_length=500)
    maitre_ouvrage: str | None = Field(default=None, max_length=200)
    wilaya_code: str | None = Field(default=None, max_length=3)
    date_limite: date | None = None
    budget_estime_da: int | None = Field(default=None, ge=0)
    qualification_requise_cat: str | None = Field(default=None, max_length=10)
    qualification_requise_activites: str | None = None
    notes: str | None = None


class AoOut(AoIn):
    id: int


class AoImportResult(BaseSchema):
    ao: AoOut
    champs_extraits: list[str]
    champs_manquants: list[str]


# ----- Audit -----
class RuleResultOut(BaseSchema):
    code: str
    libelle: str
    categorie: str
    poids: int
    verdict: str
    message: str
    action: str | None = None


class AuditOut(BaseSchema):
    ao_id: int
    score: int
    verdict_global: str
    total_ok: int
    total_warning: int
    total_danger: int
    regles: list[RuleResultOut]


# ----- Prix -----
class PrixArticleOut(BaseSchema):
    id: int
    code: str
    libelle: str
    unite: str
    categorie: str
    prix_min_da: int
    prix_moy_da: int
    prix_max_da: int


class PosteIn(BaseSchema):
    article_code: str = Field(..., max_length=40)
    quantite: float = Field(..., gt=0)
    prix_propose_da: int = Field(..., ge=0)


class PosteSimule(BaseSchema):
    article_code: str
    libelle: str
    quantite: float
    prix_propose_da: int
    prix_moy_da: int
    ecart_vs_moy_pct: float
    verdict: str  # "bas" | "ok" | "haut" | "hors_fourchette"


class SimulationIn(BaseSchema):
    postes: list[PosteIn] = Field(..., min_length=1)


class SimulationOut(BaseSchema):
    postes: list[PosteSimule]
    montant_total_propose_da: int
    montant_total_reference_da: int
    ecart_global_pct: float


# ----- Templates -----
class TemplateOut(BaseSchema):
    code: str
    nom: str
    description: str
    budget_reference_da: int


class TemplateChiffreIn(BaseSchema):
    budget_cible_da: int = Field(..., gt=0)


class PosteChiffre(BaseSchema):
    article_code: str
    libelle: str
    unite: str
    quantite: float
    prix_unitaire_da: int
    total_da: int


class TemplateChiffreOut(BaseSchema):
    code: str
    nom: str
    budget_cible_da: int
    montant_calcule_da: int
    postes: list[PosteChiffre]
