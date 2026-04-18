# -*- coding: utf-8 -*-
"""Router /signup — inscription self-service Cas 1 (entreprise) et Cas 2 (cabinet)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Cabinet, Entreprise, Organisation, User
from app.models.enums import OrgStatut, OrgType, PlanCode, UserRole
from app.schemas import SignupCabinetIn, SignupEntrepriseIn, SignupOut
from app.security import create_access_token, hash_password

router = APIRouter(prefix="/signup", tags=["signup"])


def _email_taken(db: Session, email: str) -> bool:
    return db.query(User).filter(User.email == email.lower()).first() is not None


@router.post("/entreprise", response_model=SignupOut, status_code=status.HTTP_201_CREATED)
def signup_entreprise(payload: SignupEntrepriseIn, db: Session = Depends(get_db)) -> SignupOut:
    """Inscrit une entreprise autonome Cas 1. Crée Organisation + Entreprise + User patron."""
    email = payload.email.lower()
    if _email_taken(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cet email est deja utilise."
        )

    org = Organisation(
        nom=payload.nom_entreprise,
        type=OrgType.ENTREPRISE.value,
        plan=PlanCode.DECOUVERTE.value,
        statut=OrgStatut.ACTIF.value,
    )
    db.add(org)
    db.flush()

    entreprise = Entreprise(
        organisation_id=org.id,
        nom=payload.nom_entreprise,
        forme_juridique=payload.forme_juridique,
        nif=payload.nif,
        wilaya_code=payload.wilaya_code,
        wilaya_nom=payload.wilaya_nom,
        telephone=payload.telephone,
        secteur=payload.secteur,
        email=email,
    )
    db.add(entreprise)

    user = User(
        organisation_id=org.id,
        email=email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=UserRole.PATRON.value,
        actif=True,
    )
    db.add(user)
    db.flush()

    db.commit()

    settings = get_settings()
    token = create_access_token(
        user_id=user.id,
        organisation_id=org.id,
        role=user.role,
        organisation_type=org.type,
        entreprise_id=entreprise.id,
    )
    return SignupOut(
        organisation_id=org.id,
        organisation_type=org.type,
        user_id=user.id,
        entreprise_id=entreprise.id,
        access_token=token,
        expires_in=settings.jwt_expire_hours * 3600,
    )


@router.post("/cabinet", response_model=SignupOut, status_code=status.HTTP_201_CREATED)
def signup_cabinet(payload: SignupCabinetIn, db: Session = Depends(get_db)) -> SignupOut:
    """Inscrit un cabinet de consultant Cas 2. Crée Organisation + Cabinet + User consultant."""
    email = payload.email.lower()
    if _email_taken(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cet email est deja utilise."
        )

    org = Organisation(
        nom=payload.nom_cabinet,
        type=OrgType.CABINET.value,
        plan=PlanCode.EXPERT.value,
        statut=OrgStatut.ACTIF.value,
    )
    db.add(org)
    db.flush()

    cabinet = Cabinet(
        organisation_id=org.id,
        nom=payload.nom_cabinet,
        consultant_principal=payload.consultant_principal,
        email=email,
        telephone=payload.telephone,
        wilaya_code=payload.wilaya_code,
    )
    db.add(cabinet)
    db.flush()

    user = User(
        organisation_id=org.id,
        email=email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=UserRole.CONSULTANT.value,
        actif=True,
    )
    db.add(user)
    db.flush()
    db.commit()

    settings = get_settings()
    token = create_access_token(
        user_id=user.id,
        organisation_id=org.id,
        role=user.role,
        organisation_type=org.type,
        cabinet_id=cabinet.id,
    )
    return SignupOut(
        organisation_id=org.id,
        organisation_type=org.type,
        user_id=user.id,
        cabinet_id=cabinet.id,
        access_token=token,
        expires_in=settings.jwt_expire_hours * 3600,
    )
