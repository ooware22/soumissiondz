# -*- coding: utf-8 -*-
"""Modèle Entreprise — entité métier qui soumissionne."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.cabinet import Cabinet
    from app.models.organisation import Organisation


class Entreprise(Base, TimestampMixin):
    """Entreprise algérienne cliente (Cas 1 autonome ou sous gestion Cabinet Cas 2)."""

    __tablename__ = "entreprise"
    __table_args__ = (
        UniqueConstraint("organisation_id", name="uq_entreprise_organisation"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Tenant : une entreprise Cas 1 possède sa propre Organisation (1-1).
    # Pour une entreprise gérée par un Cabinet (Cas 2), organisation_id est nullable
    # et cabinet_id pointe sur le cabinet propriétaire.
    organisation_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"), nullable=True, unique=True
    )
    cabinet_id: Mapped[int | None] = mapped_column(
        ForeignKey("cabinet.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Identité
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    forme_juridique: Mapped[str | None] = mapped_column(String(50))  # SARL, SPA, EURL, ETI...
    nif: Mapped[str | None] = mapped_column(String(30), index=True)
    nis: Mapped[str | None] = mapped_column(String(30))
    rc: Mapped[str | None] = mapped_column(String(50))
    gerant: Mapped[str | None] = mapped_column(String(200))

    # Siège
    wilaya_code: Mapped[str | None] = mapped_column(String(3))  # "16" Alger, "19" Sétif...
    wilaya_nom: Mapped[str | None] = mapped_column(String(60))
    adresse: Mapped[str | None] = mapped_column(String(300))
    telephone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(120))

    # Activité
    secteur: Mapped[str | None] = mapped_column(String(60))  # BTPH, services, fournitures...
    activite: Mapped[str | None] = mapped_column(String(300))
    effectif: Mapped[int | None] = mapped_column(Integer)
    ca_moyen_da: Mapped[int | None] = mapped_column(Integer)  # DA

    # Qualification BTPH
    qualification_cat: Mapped[str | None] = mapped_column(String(10))  # I..IX
    qualification_activites: Mapped[list | None] = mapped_column(JSON)
    qualification_expiration: Mapped[date | None] = mapped_column(Date)

    # Relations
    organisation: Mapped["Organisation | None"] = relationship(
        "Organisation", back_populates="entreprise"
    )
    cabinet: Mapped["Cabinet | None"] = relationship("Cabinet", back_populates="entreprises")

    def __repr__(self) -> str:
        return f"<Entreprise id={self.id} nom={self.nom!r}>"
