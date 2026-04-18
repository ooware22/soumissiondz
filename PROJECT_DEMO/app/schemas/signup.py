# -*- coding: utf-8 -*-
"""Schémas Pydantic — inscription self-service des 3 profils."""
from __future__ import annotations

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import BaseSchema


class _CommonUserPart(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=200)
    username: str = Field(..., min_length=2, max_length=80)


class SignupEntrepriseIn(_CommonUserPart):
    """Inscription Cas 1 : une entreprise autonome + user patron."""

    nom_entreprise: str = Field(..., min_length=2, max_length=200)
    forme_juridique: str | None = Field(default=None, max_length=50)
    nif: str | None = Field(default=None, max_length=30)
    wilaya_code: str | None = Field(default=None, max_length=3)
    wilaya_nom: str | None = Field(default=None, max_length=60)
    telephone: str | None = Field(default=None, max_length=30)
    secteur: str | None = Field(default=None, max_length=60)

    @field_validator("forme_juridique")
    @classmethod
    def _check_forme(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"SARL", "SPA", "EURL", "SNC", "ETI", "AUTO-ENTREPRENEUR", "AUTRE"}
        if v.upper() not in allowed:
            raise ValueError(f"forme_juridique doit etre parmi {sorted(allowed)}")
        return v.upper()


class SignupCabinetIn(_CommonUserPart):
    """Inscription Cas 2 : un cabinet de consultant + user consultant."""

    nom_cabinet: str = Field(..., min_length=2, max_length=200)
    consultant_principal: str = Field(..., min_length=2, max_length=200)
    telephone: str | None = Field(default=None, max_length=30)
    wilaya_code: str | None = Field(default=None, max_length=3)


class SignupOut(BaseSchema):
    organisation_id: int
    organisation_type: str
    user_id: int
    entreprise_id: int | None = None
    cabinet_id: int | None = None
    access_token: str
    token_type: str = "bearer"
    expires_in: int
