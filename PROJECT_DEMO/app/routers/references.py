# -*- coding: utf-8 -*-
"""Router /references — antecedents de marches."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import Reference
from app.schemas import MessageOut, ReferenceIn, ReferenceOut
from app.scoping import resolve_entreprise_courante

router = APIRouter(prefix="/references", tags=["references"])


@router.get("", response_model=list[ReferenceOut])
def list_refs(ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    refs = db.query(Reference).filter(Reference.entreprise_id == ent.id).all()
    return [ReferenceOut.model_validate(r) for r in refs]


@router.post("", response_model=ReferenceOut, status_code=status.HTTP_201_CREATED)
def create_ref(
    payload: ReferenceIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    ent = resolve_entreprise_courante(db, ctx)
    ref = Reference(entreprise_id=ent.id, **payload.model_dump())
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ReferenceOut.model_validate(ref)


def _find(db: Session, ctx: SecurityContext, ref_id: int) -> Reference:
    ent = resolve_entreprise_courante(db, ctx)
    r = db.get(Reference, ref_id)
    if r is None or r.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="Reference introuvable.")
    return r


@router.get("/{ref_id}", response_model=ReferenceOut)
def get_ref(ref_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    return ReferenceOut.model_validate(_find(db, ctx, ref_id))


@router.put("/{ref_id}", response_model=ReferenceOut)
def update_ref(
    ref_id: int, payload: ReferenceIn,
    ctx=Depends(get_current_context), db=Depends(get_db),
):
    r = _find(db, ctx, ref_id)
    for k, v in payload.model_dump().items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return ReferenceOut.model_validate(r)


@router.delete("/{ref_id}", response_model=MessageOut)
def delete_ref(ref_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    r = _find(db, ctx, ref_id)
    db.delete(r)
    db.commit()
    return MessageOut(detail="Reference supprimee.")
