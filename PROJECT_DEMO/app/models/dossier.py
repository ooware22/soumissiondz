# -*- coding: utf-8 -*-
"""Modeles Phase 3 (Lots 4+5) : Dossier, Caution, Soumission."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.entreprise import Entreprise
    from app.models.metier import AppelOffres
    from app.models.user import User


# 7 etapes standardisees du Kanban
ETAPES_DOSSIER = [
    "profil", "documents", "audit", "chiffrage",
    "memoire", "verification", "depot",
]
# 4 statuts Kanban
STATUTS_DOSSIER = ["a_faire", "en_cours", "a_valider", "termine"]


class Dossier(Base, TimestampMixin):
    """Preparation en cours d'une soumission — pilotee par le Kanban."""

    __tablename__ = "dossier"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ao_id: Mapped[int | None] = mapped_column(
        ForeignKey("appel_offres.id", ondelete="SET NULL"), nullable=True
    )
    preparateur_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    nom: Mapped[str] = mapped_column(String(300), nullable=False)
    etape_actuelle: Mapped[str] = mapped_column(String(30), nullable=False, default="profil")
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="a_faire")
    score_audit: Mapped[int | None] = mapped_column(Integer)
    date_cible: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)

    entreprise: Mapped["Entreprise"] = relationship("Entreprise")
    ao: Mapped["AppelOffres | None"] = relationship("AppelOffres")
    preparateur: Mapped["User | None"] = relationship("User")


# Types de cautions bancaires
TYPES_CAUTION = [
    ("caution_soumission", "Caution de soumission (~1%)"),
    ("garantie_bonne_execution", "Garantie de bonne execution (5-10%)"),
    ("retenue_garantie", "Retenue de garantie (5%)"),
]
TYPES_CAUTION_CODES = {c for c, _ in TYPES_CAUTION}


class Caution(Base, TimestampMixin):
    """Caution bancaire rattachee a un dossier ou a une soumission."""

    __tablename__ = "caution"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dossier_id: Mapped[int | None] = mapped_column(
        ForeignKey("dossier.id", ondelete="SET NULL"), nullable=True
    )
    type_code: Mapped[str] = mapped_column(String(40), nullable=False)
    banque: Mapped[str | None] = mapped_column(String(100))
    montant_da: Mapped[int] = mapped_column(Integer, nullable=False)
    date_emission: Mapped[date | None] = mapped_column(Date)
    date_recuperation_estimee: Mapped[date | None] = mapped_column(Date)
    reference_bancaire: Mapped[str | None] = mapped_column(String(100))
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="bloquee")  # bloquee|recuperee
    notes: Mapped[str | None] = mapped_column(Text)


class Soumission(Base, TimestampMixin):
    """Historique d'une soumission deposee."""

    __tablename__ = "soumission"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ao_id: Mapped[int | None] = mapped_column(
        ForeignKey("appel_offres.id", ondelete="SET NULL"), nullable=True
    )
    dossier_id: Mapped[int | None] = mapped_column(
        ForeignKey("dossier.id", ondelete="SET NULL"), nullable=True
    )
    date_depot: Mapped[date | None] = mapped_column(Date)
    rang: Mapped[int | None] = mapped_column(Integer)
    montant_soumissionne_da: Mapped[int | None] = mapped_column(Integer)
    montant_attributaire_da: Mapped[int | None] = mapped_column(Integer)
    ecart_pct: Mapped[int | None] = mapped_column(Integer)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="en_cours")  # gagne|perdu|en_cours
    raison_libre: Mapped[str | None] = mapped_column(Text)
