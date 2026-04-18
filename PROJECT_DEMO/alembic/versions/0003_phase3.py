# -*- coding: utf-8 -*-
"""Phase 3 — dossier, caution, soumission.

Revision ID: 0003_phase3
Revises: 0002_lots23
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_phase3"
down_revision: Union[str, None] = "0002_lots23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dossier",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ao_id", sa.Integer(),
                  sa.ForeignKey("appel_offres.id", ondelete="SET NULL"), nullable=True),
        sa.Column("preparateur_id", sa.Integer(),
                  sa.ForeignKey("user.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nom", sa.String(length=300), nullable=False),
        sa.Column("etape_actuelle", sa.String(length=30), nullable=False, server_default="profil"),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="a_faire"),
        sa.Column("score_audit", sa.Integer(), nullable=True),
        sa.Column("date_cible", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_dossier_entreprise_id", "dossier", ["entreprise_id"])

    op.create_table(
        "caution",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dossier_id", sa.Integer(),
                  sa.ForeignKey("dossier.id", ondelete="SET NULL"), nullable=True),
        sa.Column("type_code", sa.String(length=40), nullable=False),
        sa.Column("banque", sa.String(length=100), nullable=True),
        sa.Column("montant_da", sa.Integer(), nullable=False),
        sa.Column("date_emission", sa.Date(), nullable=True),
        sa.Column("date_recuperation_estimee", sa.Date(), nullable=True),
        sa.Column("reference_bancaire", sa.String(length=100), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="bloquee"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_caution_entreprise_id", "caution", ["entreprise_id"])

    op.create_table(
        "soumission",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ao_id", sa.Integer(),
                  sa.ForeignKey("appel_offres.id", ondelete="SET NULL"), nullable=True),
        sa.Column("dossier_id", sa.Integer(),
                  sa.ForeignKey("dossier.id", ondelete="SET NULL"), nullable=True),
        sa.Column("date_depot", sa.Date(), nullable=True),
        sa.Column("rang", sa.Integer(), nullable=True),
        sa.Column("montant_soumissionne_da", sa.Integer(), nullable=True),
        sa.Column("montant_attributaire_da", sa.Integer(), nullable=True),
        sa.Column("ecart_pct", sa.Integer(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="en_cours"),
        sa.Column("raison_libre", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_soumission_entreprise_id", "soumission", ["entreprise_id"])


def downgrade() -> None:
    op.drop_index("ix_soumission_entreprise_id", table_name="soumission")
    op.drop_table("soumission")
    op.drop_index("ix_caution_entreprise_id", table_name="caution")
    op.drop_table("caution")
    op.drop_index("ix_dossier_entreprise_id", table_name="dossier")
    op.drop_table("dossier")
