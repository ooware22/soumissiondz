# -*- coding: utf-8 -*-
"""Helper transverse : resout l'entreprise cible pour tout endpoint scope entreprise.

- Cas 1 (org type=entreprise) : l'entreprise est unique et liee a l'organisation.
- Cas 2 (org type=cabinet)    : le consultant doit passer le header
  X-Entreprise-Active-Id. L'entreprise doit appartenir au cabinet.

En cas de probleme (pas d'entreprise courante), 404 conformement au contrat
de securite G2.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.deps import SecurityContext
from app.models import Entreprise
from app.models.enums import OrgType


def resolve_entreprise_courante(db: Session, ctx: SecurityContext) -> Entreprise:
    """Renvoie l'Entreprise cible de la requete courante, ou leve 404."""
    if ctx.organisation_type == OrgType.ENTREPRISE.value:
        if ctx.entreprise_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise introuvable.")
        ent = db.get(Entreprise, ctx.entreprise_id)
        if ent is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise introuvable.")
        return ent

    if ctx.organisation_type == OrgType.CABINET.value:
        if ctx.entreprise_active_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Header X-Entreprise-Active-Id requis pour un cabinet.",
            )
        ent = db.get(Entreprise, ctx.entreprise_active_id)
        if ent is None or ent.cabinet_id != ctx.cabinet_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise introuvable.")
        return ent

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contexte non scope entreprise.")
