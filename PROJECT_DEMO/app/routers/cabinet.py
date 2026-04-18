# -*- coding: utf-8 -*-
"""Router /cabinet — Cas 2 : portefeuille d'entreprises + comparateur."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import (
    AppelOffres,
    Document,
    Dossier,
    Entreprise,
    Reference,
    Soumission,
)
from app.models.enums import OrgType
from app.schemas import (
    CabinetEntrepriseAvecIndicateurs,
    CabinetEntrepriseIn,
    CabinetEntrepriseOut,
    ComparateurEntreprise,
    ComparateurOut,
    MessageOut,
)
from app.services.rules_engine import run_audit

router = APIRouter(prefix="/cabinet", tags=["cabinet"])


def _require_cabinet(ctx: SecurityContext) -> int:
    if ctx.organisation_type != OrgType.CABINET.value or ctx.cabinet_id is None:
        raise HTTPException(status_code=403, detail="Endpoint reserve aux comptes cabinet (Cas 2).")
    return ctx.cabinet_id


@router.get("/entreprises", response_model=list[CabinetEntrepriseAvecIndicateurs])
def list_portefeuille(ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    cab_id = _require_cabinet(ctx)
    entreprises = db.query(Entreprise).filter(Entreprise.cabinet_id == cab_id).all()

    today = date.today()
    debut_mois = today.replace(day=1)

    out: list[CabinetEntrepriseAvecIndicateurs] = []
    for ent in entreprises:
        n_dossiers = (
            db.query(Dossier)
            .filter(Dossier.entreprise_id == ent.id, Dossier.statut != "termine")
            .count()
        )
        n_alertes = (
            db.query(Document)
            .filter(
                Document.entreprise_id == ent.id,
                Document.date_expiration.isnot(None),
                Document.date_expiration <= today + timedelta(days=30),
            )
            .count()
        )
        n_soum = (
            db.query(Soumission)
            .filter(
                Soumission.entreprise_id == ent.id,
                Soumission.date_depot.isnot(None),
                Soumission.date_depot >= debut_mois,
            )
            .count()
        )
        out.append(CabinetEntrepriseAvecIndicateurs(
            id=ent.id, nom=ent.nom,
            forme_juridique=ent.forme_juridique, nif=ent.nif,
            wilaya_code=ent.wilaya_code, secteur=ent.secteur,
            nb_dossiers_en_cours=n_dossiers,
            nb_alertes_documents=n_alertes,
            nb_soumissions_mois_courant=n_soum,
        ))
    return out


@router.post("/entreprises", response_model=CabinetEntrepriseOut, status_code=status.HTTP_201_CREATED)
def add_entreprise(
    payload: CabinetEntrepriseIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    cab_id = _require_cabinet(ctx)
    # cabinet_id force serveur-side (G3)
    data = payload.model_dump()
    ent = Entreprise(cabinet_id=cab_id, **data)
    db.add(ent)
    db.commit()
    db.refresh(ent)
    return CabinetEntrepriseOut.model_validate(ent)


def _find_entreprise_du_cabinet(db: Session, cab_id: int, ent_id: int) -> Entreprise:
    ent = db.get(Entreprise, ent_id)
    if ent is None or ent.cabinet_id != cab_id:
        raise HTTPException(status_code=404, detail="Entreprise introuvable.")
    return ent


@router.get("/entreprises/{ent_id}", response_model=CabinetEntrepriseOut)
def get_entreprise_du_portefeuille(
    ent_id: int, ctx=Depends(get_current_context), db=Depends(get_db)
):
    cab_id = _require_cabinet(ctx)
    ent = _find_entreprise_du_cabinet(db, cab_id, ent_id)
    return CabinetEntrepriseOut.model_validate(ent)


@router.delete("/entreprises/{ent_id}", response_model=MessageOut)
def remove_entreprise(ent_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    cab_id = _require_cabinet(ctx)
    ent = _find_entreprise_du_cabinet(db, cab_id, ent_id)
    db.delete(ent)
    db.commit()
    return MessageOut(detail="Entreprise retiree du portefeuille.")


@router.get("/comparer", response_model=ComparateurOut)
def comparer_pour_ao(
    ao_id: int,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Audit toutes les entreprises du portefeuille pour un AO et renvoie le ranking."""
    cab_id = _require_cabinet(ctx)
    # L'AO doit appartenir a l'une des entreprises du cabinet (sinon 404)
    ao = db.get(AppelOffres, ao_id)
    if ao is None:
        raise HTTPException(status_code=404, detail="AO introuvable.")
    ent_owner = db.get(Entreprise, ao.entreprise_id)
    if ent_owner is None or ent_owner.cabinet_id != cab_id:
        raise HTTPException(status_code=404, detail="AO introuvable.")

    entreprises = db.query(Entreprise).filter(Entreprise.cabinet_id == cab_id).all()
    classement: list[ComparateurEntreprise] = []
    for ent in entreprises:
        docs = db.query(Document).filter(Document.entreprise_id == ent.id).all()
        refs = db.query(Reference).filter(Reference.entreprise_id == ent.id).all()
        rep = run_audit(ent, ao, docs, refs)
        classement.append(ComparateurEntreprise(
            entreprise_id=ent.id, entreprise_nom=ent.nom,
            score=rep.score, verdict_global=rep.verdict_global,
            nb_danger=rep.total_danger, nb_warning=rep.total_warning, nb_ok=rep.total_ok,
        ))
    classement.sort(key=lambda c: c.score, reverse=True)
    return ComparateurOut(ao_id=ao_id, classement=classement)
