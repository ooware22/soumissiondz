# -*- coding: utf-8 -*-
"""Package modèles — imports eagers pour qu'Alembic voie tout le schéma."""
from app.models.base import Base, TimestampMixin
from app.models.cabinet import Cabinet
from app.models.entreprise import Entreprise
from app.models.enums import (
    ROLES_CABINET,
    ROLES_ENTREPRISE,
    OrgStatut,
    OrgType,
    PlanCode,
    UserRole,
)
from app.models.dossier import (
    ETAPES_DOSSIER,
    STATUTS_DOSSIER,
    TYPES_CAUTION,
    TYPES_CAUTION_CODES,
    Caution,
    Dossier,
    Soumission,
)
from app.models.metier import (
    DOCUMENT_TYPE_CODES,
    DOCUMENT_TYPES,
    AppelOffres,
    Document,
    PrixArticle,
    Reference,
)
from app.models.organisation import Organisation
from app.models.phase4 import (
    PLANS_SEED,
    PRESTATIONS_SEED,
    Abonnement,
    AoMandatAction,
    AssistantAgree,
    CodeParrainage,
    Commission,
    Facture,
    Mandat,
    Mission,
    MissionMessage,
    Plan,
    PrestationCatalogue,
    TicketHotline,
)
from app.models.user import User

__all__ = [
    "Base", "TimestampMixin",
    "Cabinet", "Entreprise", "Organisation", "User",
    "OrgType", "OrgStatut", "PlanCode", "UserRole",
    "ROLES_CABINET", "ROLES_ENTREPRISE",
    "Document", "Reference", "AppelOffres", "PrixArticle",
    "DOCUMENT_TYPES", "DOCUMENT_TYPE_CODES",
    "Dossier", "Caution", "Soumission",
    "ETAPES_DOSSIER", "STATUTS_DOSSIER", "TYPES_CAUTION", "TYPES_CAUTION_CODES",
    "AssistantAgree", "PrestationCatalogue", "Mandat", "Mission",
    "AoMandatAction", "MissionMessage", "PRESTATIONS_SEED",
    "Plan", "Abonnement", "Facture", "CodeParrainage", "Commission", "TicketHotline",
    "PLANS_SEED",
]
