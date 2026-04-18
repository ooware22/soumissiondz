# -*- coding: utf-8 -*-
"""Modèle Organisation — abstraction tenant (entreprise OU cabinet)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.enums import OrgStatut, OrgType, PlanCode

if TYPE_CHECKING:
    from app.models.cabinet import Cabinet
    from app.models.entreprise import Entreprise
    from app.models.user import User


class Organisation(Base, TimestampMixin):
    """Tenant SaaS. Porte le plan et le statut. Relation 1-1 avec Entreprise OU Cabinet."""

    __tablename__ = "organisation"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # OrgType
    plan: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PlanCode.DECOUVERTE.value
    )
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default=OrgStatut.ACTIF.value)

    entreprise: Mapped["Entreprise | None"] = relationship(
        "Entreprise", back_populates="organisation", uselist=False, cascade="all, delete-orphan"
    )
    cabinet: Mapped["Cabinet | None"] = relationship(
        "Cabinet", back_populates="organisation", uselist=False, cascade="all, delete-orphan"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organisation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organisation id={self.id} type={self.type} nom={self.nom!r}>"

    @property
    def is_entreprise(self) -> bool:
        return self.type == OrgType.ENTREPRISE.value

    @property
    def is_cabinet(self) -> bool:
        return self.type == OrgType.CABINET.value
