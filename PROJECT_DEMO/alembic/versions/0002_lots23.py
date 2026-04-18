# -*- coding: utf-8 -*-
"""Lot 2+3 : document, reference, appel_offres, prix_article.

Revision ID: 0002_lots23
Revises: 0001_initial
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_lots23"
down_revision: Union[str, None] = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "document",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type_code", sa.String(length=40), nullable=False),
        sa.Column("filename", sa.String(length=300), nullable=False),
        sa.Column("stored_path", sa.String(length=500), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("date_emission", sa.Date(), nullable=True),
        sa.Column("date_expiration", sa.Date(), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_document_entreprise_id", "document", ["entreprise_id"])

    op.create_table(
        "reference",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("objet", sa.String(length=300), nullable=False),
        sa.Column("maitre_ouvrage", sa.String(length=200), nullable=True),
        sa.Column("montant_da", sa.Integer(), nullable=True),
        sa.Column("annee", sa.Integer(), nullable=True),
        sa.Column("type_travaux", sa.String(length=100), nullable=True),
        sa.Column("attestation_pdf_path", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_reference_entreprise_id", "reference", ["entreprise_id"])

    op.create_table(
        "appel_offres",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("entreprise_id", sa.Integer(),
                  sa.ForeignKey("entreprise.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("objet", sa.String(length=500), nullable=False),
        sa.Column("maitre_ouvrage", sa.String(length=200), nullable=True),
        sa.Column("wilaya_code", sa.String(length=3), nullable=True),
        sa.Column("date_limite", sa.Date(), nullable=True),
        sa.Column("budget_estime_da", sa.Integer(), nullable=True),
        sa.Column("qualification_requise_cat", sa.String(length=10), nullable=True),
        sa.Column("qualification_requise_activites", sa.Text(), nullable=True),
        sa.Column("pdf_source_path", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_appel_offres_entreprise_id", "appel_offres", ["entreprise_id"])

    op.create_table(
        "prix_article",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=40), nullable=False, unique=True),
        sa.Column("libelle", sa.String(length=200), nullable=False),
        sa.Column("unite", sa.String(length=20), nullable=False),
        sa.Column("categorie", sa.String(length=40), nullable=False),
        sa.Column("prix_min_da", sa.Integer(), nullable=False),
        sa.Column("prix_moy_da", sa.Integer(), nullable=False),
        sa.Column("prix_max_da", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("prix_article")
    op.drop_index("ix_appel_offres_entreprise_id", table_name="appel_offres")
    op.drop_table("appel_offres")
    op.drop_index("ix_reference_entreprise_id", table_name="reference")
    op.drop_table("reference")
    op.drop_index("ix_document_entreprise_id", table_name="document")
    op.drop_table("document")
