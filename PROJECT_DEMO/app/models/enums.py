# -*- coding: utf-8 -*-
"""Énumérations métier partagées."""
from __future__ import annotations

from enum import StrEnum


class OrgType(StrEnum):
    ENTREPRISE = "entreprise"
    CABINET = "cabinet"


class PlanCode(StrEnum):
    DECOUVERTE = "DECOUVERTE"
    ARTISAN = "ARTISAN"
    PRO = "PRO"
    BUSINESS = "BUSINESS"
    EXPERT = "EXPERT"


class OrgStatut(StrEnum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    PILOTE = "pilote"


class UserRole(StrEnum):
    # Cas 1 — Entreprise
    PATRON = "patron"
    VALIDATEUR = "validateur"
    PREPARATEUR = "preparateur"
    LECTEUR = "lecteur"
    # Cas 2 — Cabinet
    CONSULTANT = "consultant"
    # Cas 3 — Assistance
    ASSISTANT_AGREE = "assistant_agree"
    # Plateforme
    ADMIN_PLATEFORME = "admin_plateforme"


ROLES_ENTREPRISE = {UserRole.PATRON, UserRole.VALIDATEUR, UserRole.PREPARATEUR, UserRole.LECTEUR}
ROLES_CABINET = {UserRole.CONSULTANT}
