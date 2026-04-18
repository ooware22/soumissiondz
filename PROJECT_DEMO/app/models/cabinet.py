# -*- coding: utf-8 -*-
"""Modèle Cabinet — tenant Cas 2 (consultant multi-entreprises)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.entreprise import Entreprise
    from app.models.organisation import Organisation


class Cabinet(Base, TimestampMixin):
    """Cabinet de consultant Cas 2. Une Organisation type=cabinet <-> un Cabinet (1-1)."""

    __tablename__ = "cabinet"

    id: Mapped[int] = mapped_column(primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    consultant_principal: Mapped[str | None] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(120))
    telephone: Mapped[str | None] = mapped_column(String(30))
    wilaya_code: Mapped[str | None] = mapped_column(String(3))

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="cabinet")
    entreprises: Mapped[list["Entreprise"]] = relationship(
        "Entreprise", back_populates="cabinet", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Cabinet id={self.id} nom={self.nom!r}>"
