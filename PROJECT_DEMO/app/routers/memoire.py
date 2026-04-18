# -*- coding: utf-8 -*-
"""Router /memoire + /formulaires — generation DOCX."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_context
from app.models import AppelOffres, Reference
from app.scoping import resolve_entreprise_courante
from app.services.docx_generator import FORMULAIRES, generer_memoire_technique

router_memoire = APIRouter(prefix="/memoire", tags=["memoire"])
router_formulaires = APIRouter(prefix="/formulaires", tags=["formulaires"])


DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _resolve_ao(db: Session, ctx, ao_id: int) -> AppelOffres:
    ent = resolve_entreprise_courante(db, ctx)
    ao = db.get(AppelOffres, ao_id)
    if ao is None or ao.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="AO introuvable.")
    return ao


@router_memoire.get("/generer")
def generer_memoire(
    ao_id: int, ctx=Depends(get_current_context), db: Session = Depends(get_db)
):
    ao = _resolve_ao(db, ctx, ao_id)
    refs = db.query(Reference).filter(Reference.entreprise_id == ao.entreprise_id).all()
    data = generer_memoire_technique(ao.entreprise, ao, refs)
    filename = f"memoire_technique_AO_{ao.id}.docx"
    return Response(
        content=data, media_type=DOCX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router_formulaires.get("/{code}/generer")
def generer_formulaire(
    code: str, ao_id: int,
    ctx=Depends(get_current_context), db: Session = Depends(get_db),
):
    if code not in FORMULAIRES:
        raise HTTPException(
            status_code=404,
            detail=f"Formulaire inconnu. Codes valides: {sorted(FORMULAIRES)}",
        )
    ao = _resolve_ao(db, ctx, ao_id)
    data = FORMULAIRES[code](ao.entreprise, ao)
    filename = f"{code}_AO_{ao.id}.docx"
    return Response(
        content=data, media_type=DOCX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
