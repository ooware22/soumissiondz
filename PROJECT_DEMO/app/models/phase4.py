# -*- coding: utf-8 -*-
"""Modeles Phase 4 (Lots 6+7) : Cas 3 assistance + monetisation."""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.entreprise import Entreprise
    from app.models.user import User


# =========================================================================
# CAS 3 — ASSISTANCE
# =========================================================================

class AssistantAgree(Base, TimestampMixin):
    """Assistant freelance recrute par la plateforme. Attache a un User existant."""

    __tablename__ = "assistant_agree"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    specialites: Mapped[list | None] = mapped_column(JSON)  # ["BTPH", "fournitures", ...]
    note_moyenne: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # /100
    nb_missions_terminees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cv_pdf_path: Mapped[str | None] = mapped_column(String(500))
    charte_signee_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    iban: Mapped[str | None] = mapped_column(String(50))
    rib: Mapped[str | None] = mapped_column(String(50))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["User"] = relationship("User")


class PrestationCatalogue(Base, TimestampMixin):
    """Catalogue public des prestations d'assistance."""

    __tablename__ = "prestation_catalogue"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    prix_ht_da: Mapped[int] = mapped_column(Integer, nullable=False)
    delai_max_jours: Mapped[int] = mapped_column(Integer, nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Mandat(Base, TimestampMixin):
    """Mandat de representation signe par le client (obligatoire avant action assistant)."""

    __tablename__ = "mandat"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mission_id: Mapped[int | None] = mapped_column(
        ForeignKey("mission.id", ondelete="SET NULL"), nullable=True
    )
    assistant_id: Mapped[int | None] = mapped_column(
        ForeignKey("assistant_agree.id", ondelete="SET NULL"), nullable=True
    )
    pdf_signe_path: Mapped[str | None] = mapped_column(String(500))
    signe_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    signe_ip: Mapped[str | None] = mapped_column(String(45))
    signe_user_agent: Mapped[str | None] = mapped_column(String(300))
    valide_du: Mapped[date | None] = mapped_column(Date)
    valide_jusqu_au: Mapped[date | None] = mapped_column(Date)
    perimetre_actions: Mapped[list | None] = mapped_column(JSON)
    statut: Mapped[str] = mapped_column(String(30), nullable=False, default="en_attente_signature")


class Mission(Base, TimestampMixin):
    """Mission concrete d'assistance commandee par le client."""

    __tablename__ = "mission"

    id: Mapped[int] = mapped_column(primary_key=True)
    entreprise_id: Mapped[int] = mapped_column(
        ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False, index=True
    )
    prestation_id: Mapped[int] = mapped_column(
        ForeignKey("prestation_catalogue.id", ondelete="RESTRICT"), nullable=False
    )
    ao_id: Mapped[int | None] = mapped_column(
        ForeignKey("appel_offres.id", ondelete="SET NULL"), nullable=True
    )
    assistant_id: Mapped[int | None] = mapped_column(
        ForeignKey("assistant_agree.id", ondelete="SET NULL"), nullable=True
    )
    brief: Mapped[str] = mapped_column(Text, nullable=False)
    statut: Mapped[str] = mapped_column(String(30), nullable=False, default="brouillon")
    prix_ht_da: Mapped[int] = mapped_column(Integer, nullable=False)
    tva: Mapped[int] = mapped_column(Integer, nullable=False, default=19)  # %
    prix_ttc_da: Mapped[int] = mapped_column(Integer, nullable=False)

    affectee_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    demarree_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    livree_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    validee_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    livrables: Mapped[list | None] = mapped_column(JSON)
    note_client: Mapped[int | None] = mapped_column(Integer)  # 1-5
    commentaire_client: Mapped[str | None] = mapped_column(Text)
    paiement_assistant_statut: Mapped[str] = mapped_column(String(20), nullable=False, default="du")  # du | paye


class AoMandatAction(Base, TimestampMixin):
    """Journal de chaque action effectuee par un assistant dans le cadre d'un mandat."""

    __tablename__ = "ao_mandat_action"

    id: Mapped[int] = mapped_column(primary_key=True)
    mandat_id: Mapped[int] = mapped_column(
        ForeignKey("mandat.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id_assistant: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    action_type: Mapped[str] = mapped_column(String(60), nullable=False)
    action_payload: Mapped[dict | None] = mapped_column(JSON)


class MissionMessage(Base, TimestampMixin):
    """Messagerie dediee a une mission entre client et assistant."""

    __tablename__ = "mission_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(
        ForeignKey("mission.id", ondelete="CASCADE"), nullable=False, index=True
    )
    auteur_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    role_auteur: Mapped[str] = mapped_column(String(20), nullable=False)  # client | assistant
    message: Mapped[str] = mapped_column(Text, nullable=False)


# Catalogue de prestations seed
PRESTATIONS_SEED = [
    ("MAJ_COFFRE", "Mise a jour coffre-fort", "Verification et upload des 15 documents officiels", 8000, 5),
    ("DOSSIER_CLE_EN_MAIN", "Preparation dossier cle en main", "Dossier complet AO -> depot", 35000, 7),
    ("CHIFFRAGE_DQE", "Chiffrage DQE", "Devis Quantitatif Estimatif detaille", 15000, 4),
    ("REDACTION_MEMOIRE", "Redaction memoire technique", "Memoire personnalise au projet", 12000, 3),
    ("URGENCE_72H", "Urgence < 72h", "Mission complete en moins de 72 heures (majoration)", 65000, 3),
    ("ACCOMPAGNEMENT_DEPOT", "Accompagnement depot physique", "Aide a la constitution + remise du dossier", 10000, 2),
    ("FORFAIT_MENSUEL", "Forfait mensuel suivi", "Suivi continu 1 dossier/mois", 25000, 30),
]


# =========================================================================
# MONETISATION (LOT 7)
# =========================================================================

class Plan(Base, TimestampMixin):
    """Plan tarifaire (DECOUVERTE/ARTISAN/PRO/BUSINESS/EXPERT + HOTLINE)."""

    __tablename__ = "plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prix_mensuel_da: Mapped[int] = mapped_column(Integer, nullable=False)
    prix_annuel_da: Mapped[int] = mapped_column(Integer, nullable=False)  # remise 10%
    description: Mapped[str | None] = mapped_column(Text)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


PLANS_SEED = [
    ("DECOUVERTE", "Decouverte (gratuit 14j)", 0, 0,
     "Test de la plateforme, 1 dossier, 14 jours."),
    ("ARTISAN", "Artisan", 5000, 54000,
     "TPE solo, 1 utilisateur, dossiers illimites."),
    ("PRO", "Pro", 10000, 108000,
     "PME 5-30 employes, jusqu'a 5 utilisateurs."),
    ("BUSINESS", "Business", 15000, 162000,
     "PME 30+, multi-utilisateurs sans limite."),
    ("EXPERT", "Expert (consultants)", 20000, 216000,
     "Consultants multi-entreprises, portefeuille illimite."),
    ("HOTLINE", "Hotline (add-on)", 4000, 43200,
     "Acces a la hotline support technique + conseil."),
]


class Abonnement(Base, TimestampMixin):
    """Abonnement actif d'une organisation a un plan."""

    __tablename__ = "abonnement"

    id: Mapped[int] = mapped_column(primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("plan.id", ondelete="RESTRICT"), nullable=False
    )
    periodicite: Mapped[str] = mapped_column(String(10), nullable=False, default="mensuel")  # mensuel|annuel
    debut: Mapped[date] = mapped_column(Date, nullable=False)
    fin: Mapped[date | None] = mapped_column(Date)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="actif")  # actif|suspendu|resilie


class Facture(Base, TimestampMixin):
    """Facture conforme fiscalite algerienne (NIF/NIS/RC + TVA 19%)."""

    __tablename__ = "facture"

    id: Mapped[int] = mapped_column(primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False, index=True
    )
    numero: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    abonnement_id: Mapped[int | None] = mapped_column(
        ForeignKey("abonnement.id", ondelete="SET NULL"), nullable=True
    )
    mission_id: Mapped[int | None] = mapped_column(
        ForeignKey("mission.id", ondelete="SET NULL"), nullable=True
    )
    date_emission: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date)
    libelle: Mapped[str] = mapped_column(String(300), nullable=False)
    prix_ht_da: Mapped[int] = mapped_column(Integer, nullable=False)
    tva_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=19)
    prix_ttc_da: Mapped[int] = mapped_column(Integer, nullable=False)
    mode_paiement: Mapped[str] = mapped_column(String(30), nullable=False, default="virement")  # virement|edahabia|cib|acte
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="emise")  # emise|payee|annulee
    paiement_recu_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pdf_path: Mapped[str | None] = mapped_column(String(500))


class CodeParrainage(Base, TimestampMixin):
    """Code de parrainage unique attribue a un user."""

    __tablename__ = "code_parrainage"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Commission(Base, TimestampMixin):
    """Commission de parrainage (20% recurrent plafonne 12 mois)."""

    __tablename__ = "commission"

    id: Mapped[int] = mapped_column(primary_key=True)
    parrain_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    organisation_filleule_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False
    )
    facture_id: Mapped[int | None] = mapped_column(
        ForeignKey("facture.id", ondelete="SET NULL"), nullable=True
    )
    mois: Mapped[str] = mapped_column(String(7), nullable=False)  # YYYY-MM
    montant_commission_da: Mapped[int] = mapped_column(Integer, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="due")  # due|payee


class TicketHotline(Base, TimestampMixin):
    """Ticket support hotline (technique/conseil/expertise)."""

    __tablename__ = "ticket_hotline"

    id: Mapped[int] = mapped_column(primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id_emetteur: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    user_id_operateur: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )
    niveau: Mapped[str] = mapped_column(String(20), nullable=False)  # technique|conseil|expertise
    sujet: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouvert")  # ouvert|en_cours|resolu|ferme
    reponse: Mapped[str | None] = mapped_column(Text)
    resolu_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
