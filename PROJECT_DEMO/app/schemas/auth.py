# -*- coding: utf-8 -*-
"""Schémas Pydantic — authentification."""
from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.common import BaseSchema


class LoginIn(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=200)


class TokenOut(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeOut(BaseSchema):
    user_id: int
    email: str
    username: str
    role: str
    organisation_id: int
    organisation_type: str
    organisation_nom: str
    entreprise_id: int | None = None
    cabinet_id: int | None = None
    plan: str
