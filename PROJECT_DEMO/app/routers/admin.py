# -*- coding: utf-8 -*-
"""Router /admin — actions reservees admin_plateforme.

Notamment recrutement des assistants agrees (Cas 3 — pas de signup public).
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import Organisation, User
from app.models.enums import OrgStatut, OrgType, PlanCode, UserRole
from app.models.phase4 import AssistantAgree
from app.schemas.common import BaseSchema
from app.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(ctx: SecurityContext = Depends(get_current_context)) -> SecurityContext:
    if ctx.role != UserRole.ADMIN_PLATEFORME.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action reservee a l'administration de la plateforme.",
        )
    return ctx


class AssistantRecruterIn(BaseSchema):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=80)
    password: str = Field(..., min_length=8, max_length=200)
    specialites: list[str] = Field(default_factory=list)
    iban: str | None = Field(default=None, max_length=50)
    rib: str | None = Field(default=None, max_length=50)


class AssistantOut(BaseSchema):
    id: int
    user_id: int
    email: str
    specialites: list | None = None
    note_moyenne: int
    nb_missions_terminees: int
    actif: bool


@router.post(
    "/assistants", response_model=AssistantOut, status_code=status.HTTP_201_CREATED
)
def recruter_assistant(
    payload: AssistantRecruterIn,
    _ctx: SecurityContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AssistantOut:
    """Cree un User role=assistant_agree + un AssistantAgree.

    L'assistant est rattache a une 'organisation technique' SOUMISSION.DZ
    plutot qu'a une entreprise cliente. Cette org technique est unique et
    creee a la demande au premier recrutement.
    """
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email deja utilise.")

    org_tech = (
        db.query(Organisation)
        .filter(Organisation.nom == "SOUMISSION.DZ — Assistants",
                Organisation.type == OrgType.ENTREPRISE.value)
        .one_or_none()
    )
    if org_tech is None:
        org_tech = Organisation(
            nom="SOUMISSION.DZ — Assistants",
            type=OrgType.ENTREPRISE.value,
            plan=PlanCode.BUSINESS.value,
            statut=OrgStatut.ACTIF.value,
        )
        db.add(org_tech)
        db.flush()

    user = User(
        organisation_id=org_tech.id, email=email, username=payload.username,
        password_hash=hash_password(payload.password),
        role=UserRole.ASSISTANT_AGREE.value, actif=True,
    )
    db.add(user)
    db.flush()

    asst = AssistantAgree(
        user_id=user.id, specialites=payload.specialites,
        iban=payload.iban, rib=payload.rib,
        charte_signee_at=datetime.now(timezone.utc),
        actif=True,
    )
    db.add(asst)
    db.commit()
    db.refresh(asst)
    return AssistantOut(
        id=asst.id, user_id=user.id, email=user.email,
        specialites=asst.specialites, note_moyenne=asst.note_moyenne,
        nb_missions_terminees=asst.nb_missions_terminees, actif=asst.actif,
    )


@router.get("/assistants", response_model=list[AssistantOut])
def list_assistants(
    _ctx: SecurityContext = Depends(require_admin), db: Session = Depends(get_db)
) -> list[AssistantOut]:
    rows = db.query(AssistantAgree).join(User, User.id == AssistantAgree.user_id).all()
    out = []
    for asst in rows:
        u = db.get(User, asst.user_id)
        out.append(AssistantOut(
            id=asst.id, user_id=asst.user_id, email=u.email if u else "—",
            specialites=asst.specialites, note_moyenne=asst.note_moyenne,
            nb_missions_terminees=asst.nb_missions_terminees, actif=asst.actif,
        ))
    return out
