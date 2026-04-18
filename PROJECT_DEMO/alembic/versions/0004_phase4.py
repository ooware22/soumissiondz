# -*- coding: utf-8 -*-
"""Phase 4 — Cas 3 (assistance) + monetisation.

Revision ID: 0004_phase4
Revises: 0003_phase3
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_phase4"
down_revision: Union[str, None] = "0003_phase3"
branch_labels = None
depends_on = None


def _ts():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    # ---------- Cas 3 ----------
    op.create_table(
        "assistant_agree",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("specialites", sa.JSON(), nullable=True),
        sa.Column("note_moyenne", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("nb_missions_terminees", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cv_pdf_path", sa.String(length=500), nullable=True),
        sa.Column("charte_signee_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("iban", sa.String(length=50), nullable=True),
        sa.Column("rib", sa.String(length=50), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )
    op.create_table(
        "prestation_catalogue",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("prix_ht_da", sa.Integer(), nullable=False),
        sa.Column("delai_max_jours", sa.Integer(), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )
    op.create_table(
        "mission",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prestation_id", sa.Integer(),
                  sa.ForeignKey("prestation_catalogue.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ao_id", sa.Integer(),
                  sa.ForeignKey("appel_offres.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assistant_id", sa.Integer(),
                  sa.ForeignKey("assistant_agree.id", ondelete="SET NULL"), nullable=True),
        sa.Column("brief", sa.Text(), nullable=False),
        sa.Column("statut", sa.String(length=30), nullable=False, server_default="brouillon"),
        sa.Column("prix_ht_da", sa.Integer(), nullable=False),
        sa.Column("tva", sa.Integer(), nullable=False, server_default="19"),
        sa.Column("prix_ttc_da", sa.Integer(), nullable=False),
        sa.Column("affectee_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("demarree_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("livree_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("validee_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("livrables", sa.JSON(), nullable=True),
        sa.Column("note_client", sa.Integer(), nullable=True),
        sa.Column("commentaire_client", sa.Text(), nullable=True),
        sa.Column("paiement_assistant_statut", sa.String(length=20), nullable=False, server_default="du"),
        *_ts(),
    )
    op.create_index("ix_mission_entreprise_id", "mission", ["entreprise_id"])

    op.create_table(
        "mandat",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mission_id", sa.Integer(),
                  sa.ForeignKey("mission.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assistant_id", sa.Integer(),
                  sa.ForeignKey("assistant_agree.id", ondelete="SET NULL"), nullable=True),
        sa.Column("pdf_signe_path", sa.String(length=500), nullable=True),
        sa.Column("signe_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signe_ip", sa.String(length=45), nullable=True),
        sa.Column("signe_user_agent", sa.String(length=300), nullable=True),
        sa.Column("valide_du", sa.Date(), nullable=True),
        sa.Column("valide_jusqu_au", sa.Date(), nullable=True),
        sa.Column("perimetre_actions", sa.JSON(), nullable=True),
        sa.Column("statut", sa.String(length=30), nullable=False, server_default="en_attente_signature"),
        *_ts(),
    )
    op.create_index("ix_mandat_entreprise_id", "mandat", ["entreprise_id"])

    op.create_table(
        "ao_mandat_action",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("mandat_id", sa.Integer(),
                  sa.ForeignKey("mandat.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id_assistant", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action_type", sa.String(length=60), nullable=False),
        sa.Column("action_payload", sa.JSON(), nullable=True),
        *_ts(),
    )
    op.create_index("ix_ao_mandat_action_mandat_id", "ao_mandat_action", ["mandat_id"])

    op.create_table(
        "mission_message",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("mission_id", sa.Integer(),
                  sa.ForeignKey("mission.id", ondelete="CASCADE"), nullable=False),
        sa.Column("auteur_user_id", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("role_auteur", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        *_ts(),
    )
    op.create_index("ix_mission_message_mission_id", "mission_message", ["mission_id"])

    # ---------- Lot 7 monetisation ----------
    op.create_table(
        "plan",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=30), nullable=False, unique=True),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("prix_mensuel_da", sa.Integer(), nullable=False),
        sa.Column("prix_annuel_da", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )
    op.create_table(
        "abonnement",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("organisation_id", sa.Integer(),
                  sa.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_id", sa.Integer(),
                  sa.ForeignKey("plan.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("periodicite", sa.String(length=10), nullable=False, server_default="mensuel"),
        sa.Column("debut", sa.Date(), nullable=False),
        sa.Column("fin", sa.Date(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="actif"),
        *_ts(),
    )
    op.create_index("ix_abonnement_organisation_id", "abonnement", ["organisation_id"])

    op.create_table(
        "facture",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("organisation_id", sa.Integer(),
                  sa.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False),
        sa.Column("numero", sa.String(length=30), nullable=False, unique=True),
        sa.Column("annee", sa.Integer(), nullable=False),
        sa.Column("abonnement_id", sa.Integer(),
                  sa.ForeignKey("abonnement.id", ondelete="SET NULL"), nullable=True),
        sa.Column("mission_id", sa.Integer(),
                  sa.ForeignKey("mission.id", ondelete="SET NULL"), nullable=True),
        sa.Column("date_emission", sa.Date(), nullable=False),
        sa.Column("date_echeance", sa.Date(), nullable=True),
        sa.Column("libelle", sa.String(length=300), nullable=False),
        sa.Column("prix_ht_da", sa.Integer(), nullable=False),
        sa.Column("tva_pct", sa.Integer(), nullable=False, server_default="19"),
        sa.Column("prix_ttc_da", sa.Integer(), nullable=False),
        sa.Column("mode_paiement", sa.String(length=30), nullable=False, server_default="virement"),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="emise"),
        sa.Column("paiement_recu_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pdf_path", sa.String(length=500), nullable=True),
        *_ts(),
    )
    op.create_index("ix_facture_organisation_id", "facture", ["organisation_id"])

    op.create_table(
        "code_parrainage",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("code", sa.String(length=20), nullable=False, unique=True),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )

    op.create_table(
        "commission",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("parrain_user_id", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organisation_filleule_id", sa.Integer(),
                  sa.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False),
        sa.Column("facture_id", sa.Integer(),
                  sa.ForeignKey("facture.id", ondelete="SET NULL"), nullable=True),
        sa.Column("mois", sa.String(length=7), nullable=False),
        sa.Column("montant_commission_da", sa.Integer(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="due"),
        *_ts(),
    )
    op.create_index("ix_commission_parrain_user_id", "commission", ["parrain_user_id"])

    op.create_table(
        "ticket_hotline",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("organisation_id", sa.Integer(),
                  sa.ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id_emetteur", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_id_operateur", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("niveau", sa.String(length=20), nullable=False),
        sa.Column("sujet", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="ouvert"),
        sa.Column("reponse", sa.Text(), nullable=True),
        sa.Column("resolu_at", sa.DateTime(timezone=True), nullable=True),
        *_ts(),
    )
    op.create_index("ix_ticket_hotline_organisation_id", "ticket_hotline", ["organisation_id"])


def downgrade() -> None:
    for tbl in ("ticket_hotline", "commission", "code_parrainage", "facture",
                "abonnement", "plan", "mission_message", "ao_mandat_action",
                "mandat", "mission", "prestation_catalogue", "assistant_agree"):
        op.drop_table(tbl)
