# -*- coding: utf-8 -*-
"""Schemas Phase 3 — Dossier, Caution, Soumission, Cabinet portfolio."""
from __future__ import annotations

from datetime import date

from pydantic import Field, field_validator

from app.models.dossier import (
    ETAPES_DOSSIER,
    STATUTS_DOSSIER,
    TYPES_CAUTION_CODES,
)
from app.schemas.common import BaseSchema


# ---------- Dossier ----------
class DossierIn(BaseSchema):
    nom: str = Field(..., min_length=2, max_length=300)
    ao_id: int | None = None
    preparateur_id: int | None = None
    date_cible: date | None = None
    notes: str | None = None


class DossierUpdate(BaseSchema):
    nom: str | None = Field(default=None, min_length=2, max_length=300)
    preparateur_id: int | None = None
    date_cible: date | None = None
    etape_actuelle: str | None = None
    statut: str | None = None
    notes: str | None = None

    @field_validator("etape_actuelle")
    @classmethod
    def _check_etape(cls, v):
        if v is not None and v not in ETAPES_DOSSIER:
            raise ValueError(f"etape_actuelle doit etre parmi {ETAPES_DOSSIER}")
        return v

    @field_validator("statut")
    @classmethod
    def _check_statut(cls, v):
        if v is not None and v not in STATUTS_DOSSIER:
            raise ValueError(f"statut doit etre parmi {STATUTS_DOSSIER}")
        return v


class DossierOut(BaseSchema):
    id: int
    nom: str
    ao_id: int | None
    preparateur_id: int | None
    etape_actuelle: str
    statut: str
    score_audit: int | None
    date_cible: date | None
    notes: str | None


class KanbanColonne(BaseSchema):
    statut: str
    dossiers: list[DossierOut]


class KanbanOut(BaseSchema):
    colonnes: list[KanbanColonne]


# ---------- Caution ----------
class CautionIn(BaseSchema):
    type_code: str
    montant_da: int = Field(..., ge=0)
    banque: str | None = Field(default=None, max_length=100)
    date_emission: date | None = None
    date_recuperation_estimee: date | None = None
    reference_bancaire: str | None = Field(default=None, max_length=100)
    dossier_id: int | None = None
    notes: str | None = None

    @field_validator("type_code")
    @classmethod
    def _check_type(cls, v):
        if v not in TYPES_CAUTION_CODES:
            raise ValueError(f"type_code doit etre parmi {sorted(TYPES_CAUTION_CODES)}")
        return v


class CautionOut(CautionIn):
    id: int
    statut: str


class CautionsResume(BaseSchema):
    total_bloque_da: int
    nombre_actives: int
    par_type: dict[str, int]
    alertes: list["CautionAlerte"]


class CautionAlerte(BaseSchema):
    id: int
    type_code: str
    date_recuperation_estimee: date
    jours_restants: int
    seuil: str  # "7j" | "15j" | "30j"


# ---------- Soumission historique ----------
class SoumissionIn(BaseSchema):
    ao_id: int | None = None
    dossier_id: int | None = None
    date_depot: date | None = None
    rang: int | None = Field(default=None, ge=1)
    montant_soumissionne_da: int | None = Field(default=None, ge=0)
    montant_attributaire_da: int | None = Field(default=None, ge=0)
    statut: str = "en_cours"
    raison_libre: str | None = None

    @field_validator("statut")
    @classmethod
    def _check_statut(cls, v):
        if v not in {"gagne", "perdu", "en_cours"}:
            raise ValueError("statut doit etre gagne | perdu | en_cours")
        return v


class SoumissionOut(SoumissionIn):
    id: int
    ecart_pct: int | None


# ---------- Cabinet (Cas 2) ----------
class CabinetEntrepriseIn(BaseSchema):
    nom: str = Field(..., min_length=2, max_length=200)
    forme_juridique: str | None = Field(default=None, max_length=50)
    nif: str | None = Field(default=None, max_length=30)
    nis: str | None = Field(default=None, max_length=30)
    rc: str | None = Field(default=None, max_length=50)
    gerant: str | None = Field(default=None, max_length=200)
    wilaya_code: str | None = Field(default=None, max_length=3)
    wilaya_nom: str | None = Field(default=None, max_length=60)
    telephone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=120)
    secteur: str | None = Field(default=None, max_length=60)


class CabinetEntrepriseOut(BaseSchema):
    id: int
    nom: str
    forme_juridique: str | None
    nif: str | None
    wilaya_code: str | None
    secteur: str | None


class CabinetEntrepriseAvecIndicateurs(CabinetEntrepriseOut):
    nb_dossiers_en_cours: int
    nb_alertes_documents: int
    nb_soumissions_mois_courant: int


class ComparateurEntreprise(BaseSchema):
    entreprise_id: int
    entreprise_nom: str
    score: int
    verdict_global: str
    nb_danger: int
    nb_warning: int
    nb_ok: int


class ComparateurOut(BaseSchema):
    ao_id: int
    classement: list[ComparateurEntreprise]
