# -*- coding: utf-8 -*-
"""Router /team — gestion d'équipe Cas 1 (entreprise uniquement)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, require_patron
from app.models import User
from app.models.enums import OrgType
from app.schemas import TeamInviteIn, TeamMemberOut
from app.security import hash_password

router = APIRouter(prefix="/team", tags=["team"])


@router.get("", response_model=list[TeamMemberOut])
def list_team(
    ctx: SecurityContext = Depends(require_patron), db: Session = Depends(get_db)
) -> list[TeamMemberOut]:
    """Liste les membres de l'équipe de l'entreprise du patron."""
    if ctx.organisation_type != OrgType.ENTREPRISE.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fonctionnalite reservee aux comptes entreprise.",
        )
    members = db.query(User).filter(User.organisation_id == ctx.organisation_id).all()
    return [TeamMemberOut.model_validate(m) for m in members]


@router.post("/invite", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED)
def invite_member(
    payload: TeamInviteIn,
    ctx: SecurityContext = Depends(require_patron),
    db: Session = Depends(get_db),
) -> TeamMemberOut:
    """Crée un nouvel utilisateur (validateur / préparateur / lecteur) sur l'entreprise du patron."""
    if ctx.organisation_type != OrgType.ENTREPRISE.value:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fonctionnalite reservee aux comptes entreprise.",
        )
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cet email est deja utilise."
        )

    user = User(
        organisation_id=ctx.organisation_id,  # ctx serveur — jamais payload
        email=email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        actif=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TeamMemberOut.model_validate(user)
