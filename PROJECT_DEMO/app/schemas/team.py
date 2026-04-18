# -*- coding: utf-8 -*-
"""Schémas Pydantic — gestion d'équipe Cas 1."""
from __future__ import annotations

from pydantic import EmailStr, Field, field_validator

from app.models.enums import UserRole
from app.schemas.common import BaseSchema

_INVITABLE_ROLES = {
    UserRole.VALIDATEUR.value,
    UserRole.PREPARATEUR.value,
    UserRole.LECTEUR.value,
}


class TeamInviteIn(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=80)
    password: str = Field(..., min_length=8, max_length=200)
    role: str

    @field_validator("role")
    @classmethod
    def _check_role(cls, v: str) -> str:
        if v not in _INVITABLE_ROLES:
            raise ValueError(f"role doit etre parmi {sorted(_INVITABLE_ROLES)}")
        return v


class TeamMemberOut(BaseSchema):
    id: int
    email: str
    username: str
    role: str
    actif: bool
