# -*- coding: utf-8 -*-
"""Initial schema — Lot 1 Fondation.

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-13
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organisation",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("plan", sa.String(length=20), nullable=False, server_default="DECOUVERTE"),
        sa.Column("statut", sa.String(length=20), nullable=False, server_default="actif"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_organisation_type", "organisation", ["type"])

    op.create_table(
        "cabinet",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "organisation_id",
            sa.Integer(),
            sa.ForeignKey("organisation.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("consultant_principal", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("telephone", sa.String(length=30), nullable=True),
        sa.Column("wilaya_code", sa.String(length=3), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "entreprise",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "organisation_id",
            sa.Integer(),
            sa.ForeignKey("organisation.id", ondelete="CASCADE"),
            nullable=True,
            unique=True,
        ),
        sa.Column(
            "cabinet_id",
            sa.Integer(),
            sa.ForeignKey("cabinet.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("forme_juridique", sa.String(length=50), nullable=True),
        sa.Column("nif", sa.String(length=30), nullable=True),
        sa.Column("nis", sa.String(length=30), nullable=True),
        sa.Column("rc", sa.String(length=50), nullable=True),
        sa.Column("gerant", sa.String(length=200), nullable=True),
        sa.Column("wilaya_code", sa.String(length=3), nullable=True),
        sa.Column("wilaya_nom", sa.String(length=60), nullable=True),
        sa.Column("adresse", sa.String(length=300), nullable=True),
        sa.Column("telephone", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=120), nullable=True),
        sa.Column("secteur", sa.String(length=60), nullable=True),
        sa.Column("activite", sa.String(length=300), nullable=True),
        sa.Column("effectif", sa.Integer(), nullable=True),
        sa.Column("ca_moyen_da", sa.Integer(), nullable=True),
        sa.Column("qualification_cat", sa.String(length=10), nullable=True),
        sa.Column("qualification_activites", sa.JSON(), nullable=True),
        sa.Column("qualification_expiration", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_entreprise_cabinet_id", "entreprise", ["cabinet_id"])
    op.create_index("ix_entreprise_nif", "entreprise", ["nif"])

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "organisation_id",
            sa.Integer(),
            sa.ForeignKey("organisation.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=120), nullable=False, unique=True),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("password_hash", sa.String(length=300), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_user_organisation_id", "user", ["organisation_id"])
    op.create_index("ix_user_email", "user", ["email"])


def downgrade() -> None:
    op.drop_index("ix_user_email", table_name="user")
    op.drop_index("ix_user_organisation_id", table_name="user")
    op.drop_table("user")
    op.drop_index("ix_entreprise_nif", table_name="entreprise")
    op.drop_index("ix_entreprise_cabinet_id", table_name="entreprise")
    op.drop_table("entreprise")
    op.drop_table("cabinet")
    op.drop_index("ix_organisation_type", table_name="organisation")
    op.drop_table("organisation")
