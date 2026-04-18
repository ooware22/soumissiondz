# -*- coding: utf-8 -*-
"""Routers /parrainage et /hotline — Lot 7 monetisation suite."""
from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models.phase4 import CodeParrainage, Commission, TicketHotline
from app.schemas.common import BaseSchema

router_parrainage = APIRouter(prefix="/parrainage", tags=["parrainage"])
router_hotline = APIRouter(prefix="/hotline", tags=["hotline"])


# =========================================================================
# PARRAINAGE — 20% commission recurrente plafonnee 12 mois
# =========================================================================
class CodeParrainageOut(BaseSchema):
    code: str
    actif: bool


class CommissionOut(BaseSchema):
    id: int
    mois: str
    montant_commission_da: int
    statut: str


@router_parrainage.get("/mon-code", response_model=CodeParrainageOut)
def mon_code(ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)):
    """Genere le code de parrainage du user a la premiere demande, sinon le renvoie."""
    code = db.query(CodeParrainage).filter(CodeParrainage.user_id == ctx.user_id).one_or_none()
    if code is None:
        code = CodeParrainage(
            user_id=ctx.user_id,
            code=f"SDZ-{secrets.token_hex(4).upper()}",
            actif=True,
        )
        db.add(code)
        db.commit()
        db.refresh(code)
    return CodeParrainageOut(code=code.code, actif=code.actif)


@router_parrainage.get("/mes-commissions", response_model=list[CommissionOut])
def mes_commissions(
    ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)
):
    rows = (
        db.query(Commission)
        .filter(Commission.parrain_user_id == ctx.user_id)
        .order_by(Commission.mois.desc())
        .all()
    )
    return [CommissionOut.model_validate(r) for r in rows]


# =========================================================================
# HOTLINE — tickets de support (3 niveaux)
# =========================================================================
class TicketIn(BaseSchema):
    niveau: str = Field(..., pattern="^(technique|conseil|expertise)$")
    sujet: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)


class TicketOut(BaseSchema):
    id: int
    niveau: str
    sujet: str
    description: str
    statut: str
    reponse: str | None = None


class TicketRepondreIn(BaseSchema):
    reponse: str = Field(..., min_length=5, max_length=10000)


@router_hotline.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def creer_ticket(
    payload: TicketIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    t = TicketHotline(
        organisation_id=ctx.organisation_id, user_id_emetteur=ctx.user_id,
        niveau=payload.niveau, sujet=payload.sujet, description=payload.description,
        statut="ouvert",
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return TicketOut.model_validate(t)


@router_hotline.get("", response_model=list[TicketOut])
def list_tickets(
    ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)
):
    rows = db.query(TicketHotline).filter(TicketHotline.organisation_id == ctx.organisation_id).all()
    return [TicketOut.model_validate(t) for t in rows]


@router_hotline.post("/{ticket_id}/repondre", response_model=TicketOut)
def repondre(
    ticket_id: int, payload: TicketRepondreIn,
    ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db),
):
    """Endpoint operateur — pour l'instant accessible a admin_plateforme uniquement."""
    from app.models.enums import UserRole
    if ctx.role != UserRole.ADMIN_PLATEFORME.value:
        raise HTTPException(status_code=403, detail="Action operateur uniquement.")
    t = db.get(TicketHotline, ticket_id)
    if t is None:
        raise HTTPException(status_code=404, detail="Ticket introuvable.")
    from datetime import datetime, timezone
    t.reponse = payload.reponse
    t.user_id_operateur = ctx.user_id
    t.statut = "resolu"
    t.resolu_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(t)
    return TicketOut.model_validate(t)
