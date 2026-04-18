# -*- coding: utf-8 -*-
"""Router /auth — login + /me."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import Entreprise, User
from app.schemas import LoginIn, MeOut, TokenOut
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    """Authentifie un user et renvoie un JWT."""
    email = payload.email.lower()
    user = db.query(User).filter(User.email == email).one_or_none()
    # Vérifie le hash même si user absent pour éviter timing attack
    dummy = "pbkdf2$200000$YWJjZGVmZ2hpamtsbW5vcA==$" + "A" * 44
    if user is None:
        verify_password(payload.password, dummy)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect."
        )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect."
        )
    if not user.actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Compte desactive."
        )

    org = user.organisation
    cabinet_id = org.cabinet.id if org.is_cabinet and org.cabinet else None
    entreprise_id = None
    if org.is_entreprise:
        ent = db.query(Entreprise).filter(Entreprise.organisation_id == org.id).one_or_none()
        entreprise_id = ent.id if ent else None

    token = create_access_token(
        user_id=user.id,
        organisation_id=org.id,
        role=user.role,
        organisation_type=org.type,
        cabinet_id=cabinet_id,
        entreprise_id=entreprise_id,
    )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    settings = get_settings()
    return TokenOut(access_token=token, expires_in=settings.jwt_expire_hours * 3600)


@router.get("/me", response_model=MeOut)
def me(ctx: SecurityContext = Depends(get_current_context)) -> MeOut:
    """Renvoie les informations du user authentifié."""
    return MeOut(
        user_id=ctx.user_id,
        email=ctx.user.email,
        username=ctx.user.username,
        role=ctx.role,
        organisation_id=ctx.organisation_id,
        organisation_type=ctx.organisation_type,
        organisation_nom=ctx.organisation.nom,
        entreprise_id=ctx.entreprise_id,
        cabinet_id=ctx.cabinet_id,
        plan=ctx.organisation.plan,
    )
