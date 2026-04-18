# -*- coding: utf-8 -*-
"""Dépendances FastAPI — contexte de sécurité (get_current_context)."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Entreprise, Organisation, User
from app.models.enums import OrgType
from app.security import JWTError, decode_access_token

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class SecurityContext:
    """Contexte de sécurité d'une requête authentifiée.

    Filtrage à appliquer sur les queries métier :
      - Cas 1 entreprise : filtrer sur entreprise_id == ctx.entreprise_id
      - Cas 2 cabinet    : filtrer sur cabinet_id == ctx.cabinet_id
                           + entreprise_id == ctx.entreprise_active_id (si précisé)
    """

    user_id: int
    user: User
    organisation_id: int
    organisation: Organisation
    organisation_type: str
    role: str
    cabinet_id: int | None = None
    entreprise_id: int | None = None  # Cas 1 = toujours défini ; Cas 2 = None
    entreprise_active_id: int | None = None  # Cas 2 uniquement (header)

    @property
    def is_cas1(self) -> bool:
        return self.organisation_type == OrgType.ENTREPRISE.value

    @property
    def is_cas2(self) -> bool:
        return self.organisation_type == OrgType.CABINET.value


def get_current_context(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    x_entreprise_active_id: int | None = Header(default=None, alias="X-Entreprise-Active-Id"),
    db: Session = Depends(get_db),
) -> SecurityContext:
    """Dépendance FastAPI — résout l'utilisateur courant à partir du JWT Bearer."""
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(creds.credentials)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalide: {e}.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["uid"])
    user = db.get(User, user_id)
    if user is None or not user.actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable ou inactif."
        )

    org = db.get(Organisation, user.organisation_id)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Organisation introuvable."
        )

    entreprise_id: int | None = None
    cabinet_id: int | None = None
    if org.is_entreprise:
        ent = db.query(Entreprise).filter(Entreprise.organisation_id == org.id).one_or_none()
        entreprise_id = ent.id if ent else None
    elif org.is_cabinet:
        cab = org.cabinet
        cabinet_id = cab.id if cab else None

    # Validation du header X-Entreprise-Active-Id pour le Cas 2
    entreprise_active_id: int | None = None
    if org.is_cabinet and x_entreprise_active_id is not None:
        ent = db.get(Entreprise, x_entreprise_active_id)
        if ent is None or ent.cabinet_id != cabinet_id:
            # Sécurité : 404 (pas 403) pour masquer l'existence
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entreprise active introuvable.",
            )
        entreprise_active_id = ent.id

    return SecurityContext(
        user_id=user.id,
        user=user,
        organisation_id=org.id,
        organisation=org,
        organisation_type=org.type,
        role=user.role,
        cabinet_id=cabinet_id,
        entreprise_id=entreprise_id,
        entreprise_active_id=entreprise_active_id,
    )


def require_patron(ctx: SecurityContext = Depends(get_current_context)) -> SecurityContext:
    """Restreint un endpoint au rôle 'patron' d'une entreprise Cas 1."""
    from app.models.enums import UserRole

    if ctx.role != UserRole.PATRON.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action reservee au patron de l'entreprise.",
        )
    return ctx
