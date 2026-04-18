# -*- coding: utf-8 -*-
"""Router /coffre — coffre-fort documentaire entreprise (15 types officiels)."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import DOCUMENT_TYPE_CODES, DOCUMENT_TYPES, Document
from app.schemas import (
    AlerteDocOut,
    DocumentOut,
    DocumentTypeOut,
    DocumentUpdateIn,
    MessageOut,
)
from app.scoping import resolve_entreprise_courante

router = APIRouter(prefix="/coffre", tags=["coffre"])


@router.get("/types", response_model=list[DocumentTypeOut])
def list_types() -> list[DocumentTypeOut]:
    """Catalogue des 15 types officiels de documents algeriens (public)."""
    return [DocumentTypeOut(code=c, libelle=l) for c, l in DOCUMENT_TYPES]


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)
) -> list[DocumentOut]:
    ent = resolve_entreprise_courante(db, ctx)
    docs = db.query(Document).filter(Document.entreprise_id == ent.id).all()
    return [DocumentOut.model_validate(d) for d in docs]


@router.post("/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    type_code: str = Form(...),
    file: UploadFile = File(...),
    date_emission: date | None = Form(default=None),
    date_expiration: date | None = Form(default=None),
    commentaire: str | None = Form(default=None),
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> DocumentOut:
    if type_code not in DOCUMENT_TYPE_CODES:
        raise HTTPException(
            status_code=422,
            detail=f"Type document inconnu. Codes autorises: {sorted(DOCUMENT_TYPE_CODES)}",
        )
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Seuls les fichiers PDF sont acceptes.")

    ent = resolve_entreprise_courante(db, ctx)

    content = await file.read()
    settings = get_settings()
    dest_dir = settings.storage_path / str(ent.id) / "documents"
    dest_dir.mkdir(parents=True, exist_ok=True)

    # On cree en DB d'abord pour avoir l'id, puis on ecrit le fichier avec l'id en prefixe.
    doc = Document(
        entreprise_id=ent.id,
        type_code=type_code,
        filename=file.filename,
        stored_path="",  # mise a jour apres
        size_bytes=len(content),
        date_emission=date_emission,
        date_expiration=date_expiration,
        commentaire=commentaire,
    )
    db.add(doc)
    db.flush()

    stored = dest_dir / f"{doc.id}_{Path(file.filename).name}"
    stored.write_bytes(content)
    doc.stored_path = str(stored)
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)


def _find_doc_for_current(db: Session, ctx: SecurityContext, doc_id: int) -> Document:
    ent = resolve_entreprise_courante(db, ctx)
    doc = db.get(Document, doc_id)
    if doc is None or doc.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="Document introuvable.")  # G2 : 404 pas 403
    return doc


@router.get("/documents/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: int,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> DocumentOut:
    return DocumentOut.model_validate(_find_doc_for_current(db, ctx, doc_id))


@router.patch("/documents/{doc_id}", response_model=DocumentOut)
def update_document(
    doc_id: int,
    payload: DocumentUpdateIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> DocumentOut:
    doc = _find_doc_for_current(db, ctx, doc_id)
    if payload.date_emission is not None:
        doc.date_emission = payload.date_emission
    if payload.date_expiration is not None:
        doc.date_expiration = payload.date_expiration
    if payload.commentaire is not None:
        doc.commentaire = payload.commentaire
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)


@router.get("/documents/{doc_id}/download")
def download_document(
    doc_id: int,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    doc = _find_doc_for_current(db, ctx, doc_id)
    path = Path(doc.stored_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Fichier manquant sur disque.")
    return FileResponse(path, filename=doc.filename, media_type="application/pdf")


@router.delete("/documents/{doc_id}", response_model=MessageOut)
def delete_document(
    doc_id: int,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
) -> MessageOut:
    doc = _find_doc_for_current(db, ctx, doc_id)
    try:
        Path(doc.stored_path).unlink(missing_ok=True)
    except OSError:
        pass
    db.delete(doc)
    db.commit()
    return MessageOut(detail="Document supprime.")


@router.get("/alertes", response_model=list[AlerteDocOut])
def alertes_expiration(
    ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)
) -> list[AlerteDocOut]:
    ent = resolve_entreprise_courante(db, ctx)
    today = date.today()
    docs = (
        db.query(Document)
        .filter(Document.entreprise_id == ent.id, Document.date_expiration.isnot(None))
        .all()
    )
    alertes: list[AlerteDocOut] = []
    for d in docs:
        assert d.date_expiration is not None
        delta = (d.date_expiration - today).days
        if delta > 30:
            continue
        if delta < 0:
            seuil = "expire"
        elif delta <= 7:
            seuil = "7j"
        elif delta <= 15:
            seuil = "15j"
        else:
            seuil = "30j"
        alertes.append(AlerteDocOut(
            id=d.id, type_code=d.type_code,
            date_expiration=d.date_expiration, jours_restants=delta, seuil=seuil,
        ))
    alertes.sort(key=lambda a: a.jours_restants)
    return alertes
