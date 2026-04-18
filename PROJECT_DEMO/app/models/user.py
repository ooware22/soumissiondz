# -*- coding: utf-8 -*-
"""Modèle User — utilisateur authentifiable, rattaché à une Organisation."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organisation import Organisation


class User(Base, TimestampMixin):
    """Utilisateur. Appartient à une Organisation (entreprise OU cabinet)."""

    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id", ondelete="CASCADE"), nullable=False, index=True
    )

    email: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(80), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(300), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)  # UserRole
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
