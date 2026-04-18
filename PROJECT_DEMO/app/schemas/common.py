# -*- coding: utf-8 -*-
"""Schémas Pydantic — enveloppes génériques."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base pour tous les schémas. Autorise la conversion depuis un ORM object."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class MessageOut(BaseSchema):
    detail: str
