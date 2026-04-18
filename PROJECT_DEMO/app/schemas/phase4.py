# -*- coding: utf-8 -*-
"""Schemas Phase 4 — assistance Cas 3 + monetisation Lot 7."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import Field, field_validator

from app.schemas.common import BaseSchema


# ---------- Cas 3 — Catalogue prestations (public) ----------
class PrestationOut(BaseSchema):
    id: int
    code: str
    nom: str
    description: str
    prix_ht_da: int
    delai_max_jours: int
    actif: bool


# ---------- Mission ----------
class MissionDemandeIn(BaseSchema):
    prestation_code: str = Field(..., max_length=50)
    brief: str = Field(..., min_length=10, max_length=5000)
    ao_id: int | None = None


class MandatSignatureIn(BaseSchema):
    accepte: bool
    valide_jours: int = Field(default=14, ge=1, le=90)


class MissionOut(BaseSchema):
    id: int
    prestation_id: int
    ao_id: int | None
    assistant_id: int | None
    brief: str
    statut: str
    prix_ht_da: int
    tva: int
    prix_ttc_da: int
    affectee_at: datetime | None
    livree_at: datetime | None
    validee_at: datetime | None
    note_client: int | None


class MissionLivraisonIn(BaseSchema):
    livrables: list[str] = Field(default_factory=list)


class MissionValidationIn(BaseSchema):
    note: int = Field(..., ge=1, le=5)
    commentaire: str | None = None


class MissionContestationIn(BaseSchema):
    motif: str = Field(..., min_length=10, max_length=2000)


class MandatOut(BaseSchema):
    id: int
    entreprise_id: int
    mission_id: int | None
    assistant_id: int | None
    statut: str
    signe_at: datetime | None
    valide_du: date | None
    valide_jusqu_au: date | None


# ---------- Assistant agree (admin) ----------
class AssistantInscriptionIn(BaseSchema):
    email: str
    username: str = Field(..., min_length=2, max_length=80)
    password: str = Field(..., min_length=8, max_length=200)
    specialites: list[str] = Field(default_factory=list)
    iban: str | None = Field(default=None, max_length=50)


class AssistantOut(BaseSchema):
    id: int
    user_id: int
    specialites: list | None
    note_moyenne: int
    nb_missions_terminees: int
    actif: bool


# ---------- Messagerie ----------
class MessageIn(BaseSchema):
    message: str = Field(..., min_length=1, max_length=5000)


class MessageOut2(BaseSchema):
    id: int
    auteur_user_id: int | None
    role_auteur: str
    message: str
    created_at: datetime


# ---------- Journal actions mandat ----------
class ActionMandatOut(BaseSchema):
    id: int
    mandat_id: int
    user_id_assistant: int | None
    action_type: str
    action_payload: dict | None
    created_at: datetime


# ---------- Plans / abonnements / factures (Lot 7) ----------
class PlanOut(BaseSchema):
    id: int
    code: str
    nom: str
    prix_mensuel_da: int
    prix_annuel_da: int
    description: str | None
    actif: bool


class AbonnementSouscrireIn(BaseSchema):
    plan_code: str
    periodicite: str = "mensuel"

    @field_validator("periodicite")
    @classmethod
    def _check_per(cls, v):
        if v not in {"mensuel", "annuel"}:
            raise ValueError("periodicite doit etre mensuel ou annuel")
        return v


class AbonnementOut(BaseSchema):
    id: int
    organisation_id: int
    plan_id: int
    periodicite: str
    debut: date
    fin: date | None
    statut: str


class FactureOut(BaseSchema):
    id: int
    numero: str
    annee: int
    date_emission: date
    date_echeance: date | None
    libelle: str
    prix_ht_da: int
    tva_pct: int
    prix_ttc_da: int
    mode_paiement: str
    statut: str


# ---------- Parrainage ----------
class CodeParrainageOut(BaseSchema):
    id: int
    code: str
    actif: bool


class CommissionOut(BaseSchema):
    id: int
    parrain_user_id: int
    organisation_filleule_id: int
    mois: str
    montant_commission_da: int
    statut: str


# ---------- Hotline ----------
class TicketIn(BaseSchema):
    niveau: str
    sujet: str = Field(..., min_length=3, max_length=300)
    description: str = Field(..., min_length=10, max_length=5000)

    @field_validator("niveau")
    @classmethod
    def _check_niveau(cls, v):
        if v not in {"technique", "conseil", "expertise"}:
            raise ValueError("niveau doit etre technique|conseil|expertise")
        return v


class TicketOut(BaseSchema):
    id: int
    niveau: str
    sujet: str
    description: str
    statut: str
    reponse: str | None
    created_at: datetime


class TicketReponseIn(BaseSchema):
    reponse: str = Field(..., min_length=1, max_length=5000)
