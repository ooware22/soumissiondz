# -*- coding: utf-8 -*-
"""Router /ao — appels d'offres, import PDF, audit de conformite."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import AppelOffres, Document, Reference
from app.schemas import (
    AoImportResult,
    AoIn,
    AoOut,
    AuditOut,
    MessageOut,
    RuleResultOut,
)
from app.scoping import resolve_entreprise_courante
from app.services.pdf_extractor import extract_from_pdf_bytes
from app.services.rules_engine import run_audit

router = APIRouter(prefix="/ao", tags=["ao"])


@router.get("", response_model=list[AoOut])
def list_ao(ctx=Depends(get_current_context), db=Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    rows = db.query(AppelOffres).filter(AppelOffres.entreprise_id == ent.id).all()
    return [AoOut.model_validate(a) for a in rows]


@router.post("", response_model=AoOut, status_code=status.HTTP_201_CREATED)
def create_ao(payload: AoIn, ctx=Depends(get_current_context), db=Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    ao = AppelOffres(entreprise_id=ent.id, **payload.model_dump())
    db.add(ao)
    db.commit()
    db.refresh(ao)
    return AoOut.model_validate(ao)


def _find_ao(db: Session, ctx: SecurityContext, ao_id: int) -> AppelOffres:
    ent = resolve_entreprise_courante(db, ctx)
    ao = db.get(AppelOffres, ao_id)
    if ao is None or ao.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="Appel d'offres introuvable.")
    return ao


@router.get("/{ao_id}", response_model=AoOut)
def get_ao(ao_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    return AoOut.model_validate(_find_ao(db, ctx, ao_id))


@router.put("/{ao_id}", response_model=AoOut)
def update_ao(ao_id: int, payload: AoIn, ctx=Depends(get_current_context), db=Depends(get_db)):
    ao = _find_ao(db, ctx, ao_id)
    for k, v in payload.model_dump().items():
        setattr(ao, k, v)
    db.commit()
    db.refresh(ao)
    return AoOut.model_validate(ao)


@router.delete("/{ao_id}", response_model=MessageOut)
def delete_ao(ao_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    ao = _find_ao(db, ctx, ao_id)
    db.delete(ao)
    db.commit()
    return MessageOut(detail="AO supprime.")


@router.post("/import-pdf", response_model=AoImportResult, status_code=status.HTTP_201_CREATED)
async def import_pdf(
    file: UploadFile = File(...),
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> AoImportResult:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Fichier PDF attendu.")
    ent = resolve_entreprise_courante(db, ctx)
    content = await file.read()

    extraction = extract_from_pdf_bytes(content)

    settings = get_settings()
    dest_dir = settings.storage_path / str(ent.id) / "ao"
    dest_dir.mkdir(parents=True, exist_ok=True)

    ao = AppelOffres(
        entreprise_id=ent.id,
        reference=extraction.reference,
        objet=extraction.objet or f"AO importe depuis {file.filename}",
        maitre_ouvrage=extraction.maitre_ouvrage,
        wilaya_code=extraction.wilaya_code,
        date_limite=extraction.date_limite,
        budget_estime_da=extraction.budget_estime_da,
        qualification_requise_cat=extraction.qualification_requise_cat,
    )
    db.add(ao)
    db.flush()

    stored = dest_dir / f"{ao.id}_{Path(file.filename).name}"
    stored.write_bytes(content)
    ao.pdf_source_path = str(stored)
    db.commit()
    db.refresh(ao)

    extracted_fields = []
    missing_fields = []
    for field in ("reference", "objet", "maitre_ouvrage", "wilaya_code",
                  "date_limite", "budget_estime_da", "qualification_requise_cat"):
        val = getattr(extraction, field)
        if val is not None:
            extracted_fields.append(field)
        else:
            missing_fields.append(field)

    return AoImportResult(
        ao=AoOut.model_validate(ao),
        champs_extraits=extracted_fields,
        champs_manquants=missing_fields,
    )


@router.get("/{ao_id}/audit", response_model=AuditOut)
def audit_ao(ao_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    ao = _find_ao(db, ctx, ao_id)
    ent = ao.entreprise
    docs = db.query(Document).filter(Document.entreprise_id == ent.id).all()
    refs = db.query(Reference).filter(Reference.entreprise_id == ent.id).all()

    report = run_audit(ent, ao, docs, refs)
    return AuditOut(
        ao_id=ao.id,
        score=report.score,
        verdict_global=report.verdict_global,
        total_ok=report.total_ok,
        total_warning=report.total_warning,
        total_danger=report.total_danger,
        regles=[RuleResultOut(
            code=r.code, libelle=r.libelle, categorie=r.categorie,
            poids=r.poids, verdict=r.verdict, message=r.message, action=r.action,
        ) for r in report.regles],
    )
