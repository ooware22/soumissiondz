# -*- coding: utf-8 -*-
"""Modeles metier Lots 2+3 : Document, Reference, AppelOffres, PrixArticle."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.entreprise import Entreprise


# 15 types officiels documents algeriens
DOCUMENT_TYPES = [
    ("CNAS", "Attestation CNAS (securite sociale salaries)"),
    ("CASNOS", "Attestation CASNOS (securite sociale non salaries)"),
    ("CACOBATPH", "Attestation CACOBATPH (conges payes BTPH)"),
    ("NIF", "Numero d'identification fiscale"),
    ("NIS", "Numero d'identification statistique"),
    ("EXTRAIT_ROLE", "Extrait de role fiscal"),
    ("ATTESTATION_FISCALE", "Attestation fiscale"),
    ("RC", "Registre du commerce"),
    ("STATUTS", "Statuts de la societe"),
    ("CASIER_JUDICIAIRE", "Casier judiciaire du gerant"),
    ("BILAN_2022", "Bilan financier 2022"),
    ("BILAN_2023", "Bilan financier 2023"),
    ("BILAN_2024", "Bilan financier 2024"),
    ("QUALIFICATION_BTPH", "Certificat de qualification BTPH"),
    ("ATTESTATION_BANCAIRE", "Attestation bancaire"),
]
DOCUMENT_TYPE_CODES = {code for code, _ in DOCUMENT_TYPES}


class Document(Base, TimestampMixin):
    """Document officiel stocke dans le coffre-fort d'une entreprise."""

    __tablename__ = "document"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type_code: Mapped[str] = mapped_column(String(40), nullable=False)  # ex: "CNAS"
    filename: Mapped[str] = mapped_column(String(300), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(500), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_emission: Mapped[date | None] = mapped_column(Date)
    date_expiration: Mapped[date | None] = mapped_column(Date)
    commentaire: Mapped[str | None] = mapped_column(Text)

    entreprise: Mapped["Entreprise"] = relationship("Entreprise")


class Reference(Base, TimestampMixin):
    """Reference de marche deja execute par une entreprise."""

    __tablename__ = "reference"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    objet: Mapped[str] = mapped_column(String(300), nullable=False)
    maitre_ouvrage: Mapped[str | None] = mapped_column(String(200))
    montant_da: Mapped[int | None] = mapped_column(Integer)
    annee: Mapped[int | None] = mapped_column(Integer)
    type_travaux: Mapped[str | None] = mapped_column(String(100))
    attestation_pdf_path: Mapped[str | None] = mapped_column(String(500))

    entreprise: Mapped["Entreprise"] = relationship("Entreprise")


class AppelOffres(Base, TimestampMixin):
    """Appel d'offres importe et rattache a une entreprise."""

    __tablename__ = "appel_offres"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reference: Mapped[str | None] = mapped_column(String(100))
    objet: Mapped[str] = mapped_column(String(500), nullable=False)
    maitre_ouvrage: Mapped[str | None] = mapped_column(String(200))
    wilaya_code: Mapped[str | None] = mapped_column(String(3))
    date_limite: Mapped[date | None] = mapped_column(Date)
    budget_estime_da: Mapped[int | None] = mapped_column(Integer)
    qualification_requise_cat: Mapped[str | None] = mapped_column(String(10))
    qualification_requise_activites: Mapped[str | None] = mapped_column(Text)
    pdf_source_path: Mapped[str | None] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)

    entreprise: Mapped["Entreprise"] = relationship("Entreprise")


class PrixArticle(Base, TimestampMixin):
    """Article du catalogue BTPH — fourchettes de prix observees sur le marche algerien."""

    __tablename__ = "prix_article"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    libelle: Mapped[str] = mapped_column(String(200), nullable=False)
    unite: Mapped[str] = mapped_column(String(20), nullable=False)
    categorie: Mapped[str] = mapped_column(String(40), nullable=False)
    prix_min_da: Mapped[int] = mapped_column(Integer, nullable=False)
    prix_moy_da: Mapped[int] = mapped_column(Integer, nullable=False)
    prix_max_da: Mapped[int] = mapped_column(Integer, nullable=False)
