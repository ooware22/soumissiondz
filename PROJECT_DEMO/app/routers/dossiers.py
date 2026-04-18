# -*- coding: utf-8 -*-
"""Routers Phase 3 : dossiers (Kanban + workflow), cautions, soumissions historique."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import (
    AppelOffres,
    Caution,
    Document,
    Dossier,
    Reference,
    Soumission,
)
from app.models.dossier import ETAPES_DOSSIER, STATUTS_DOSSIER
from app.models.enums import UserRole
from app.schemas import (
    CautionAlerte,
    CautionIn,
    CautionOut,
    CautionsResume,
    DossierIn,
    DossierOut,
    DossierUpdate,
    KanbanColonne,
    KanbanOut,
    MessageOut,
    SoumissionIn,
    SoumissionOut,
)
from app.scoping import resolve_entreprise_courante
from app.services.rules_engine import run_audit

# =========================================================================
# DOSSIERS + KANBAN + WORKFLOW
# =========================================================================
router_dossiers = APIRouter(prefix="/dossiers", tags=["dossiers"])


@router_dossiers.get("", response_model=list[DossierOut])
def list_dossiers(ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    rows = db.query(Dossier).filter(Dossier.entreprise_id == ent.id).all()
    return [DossierOut.model_validate(d) for d in rows]


@router_dossiers.post("", response_model=DossierOut, status_code=status.HTTP_201_CREATED)
def create_dossier(
    payload: DossierIn, ctx=Depends(get_current_context), db: Session = Depends(get_db)
):
    ent = resolve_entreprise_courante(db, ctx)
    # Si ao_id fourni : verifier qu'il appartient bien a l'entreprise (G2)
    if payload.ao_id is not None:
        ao = db.get(AppelOffres, payload.ao_id)
        if ao is None or ao.entreprise_id != ent.id:
            raise HTTPException(status_code=404, detail="AO introuvable.")
    d = Dossier(entreprise_id=ent.id, **payload.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return DossierOut.model_validate(d)


def _find_dossier(db: Session, ctx: SecurityContext, dossier_id: int) -> Dossier:
    ent = resolve_entreprise_courante(db, ctx)
    d = db.get(Dossier, dossier_id)
    if d is None or d.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="Dossier introuvable.")
    return d


@router_dossiers.get("/kanban", response_model=KanbanOut)
def kanban_view(ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    rows = db.query(Dossier).filter(Dossier.entreprise_id == ent.id).all()
    cols = []
    for s in STATUTS_DOSSIER:
        cols.append(KanbanColonne(
            statut=s,
            dossiers=[DossierOut.model_validate(d) for d in rows if d.statut == s],
        ))
    return KanbanOut(colonnes=cols)


@router_dossiers.get("/{dossier_id}", response_model=DossierOut)
def get_dossier(dossier_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    return DossierOut.model_validate(_find_dossier(db, ctx, dossier_id))


@router_dossiers.patch("/{dossier_id}", response_model=DossierOut)
def update_dossier(
    dossier_id: int, payload: DossierUpdate,
    ctx=Depends(get_current_context), db=Depends(get_db),
):
    d = _find_dossier(db, ctx, dossier_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    return DossierOut.model_validate(d)


@router_dossiers.post("/{dossier_id}/avancer", response_model=DossierOut)
def avancer_etape(dossier_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    """Passe le dossier a l'etape suivante (ordre fixe 7 etapes)."""
    d = _find_dossier(db, ctx, dossier_id)
    try:
        idx = ETAPES_DOSSIER.index(d.etape_actuelle)
    except ValueError:
        idx = -1
    if idx == len(ETAPES_DOSSIER) - 1:
        raise HTTPException(status_code=409, detail="Dossier deja a la derniere etape (depot).")
    d.etape_actuelle = ETAPES_DOSSIER[idx + 1]
    if d.statut == "a_faire":
        d.statut = "en_cours"
    db.commit()
    db.refresh(d)
    return DossierOut.model_validate(d)


@router_dossiers.post("/{dossier_id}/valider", response_model=DossierOut)
def valider_workflow(dossier_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    """Workflow 3 niveaux : preparateur -> validateur -> patron.

    Le rôle du current user determine le statut cible :
      - preparateur : 'en_cours' -> 'a_valider'
      - validateur  : 'a_valider' -> 'a_valider' (ack — patron doit valider)
      - patron      : 'a_valider' -> 'termine'
    """
    d = _find_dossier(db, ctx, dossier_id)
    role = ctx.role
    if role == UserRole.PREPARATEUR.value:
        if d.statut != "en_cours":
            raise HTTPException(status_code=409, detail="Dossier doit etre 'en_cours' pour passer 'a_valider'.")
        d.statut = "a_valider"
    elif role == UserRole.VALIDATEUR.value:
        if d.statut != "a_valider":
            raise HTTPException(status_code=409, detail="Dossier doit etre 'a_valider' pour validation intermediaire.")
        # Pas de changement de statut — le patron tranche
        return DossierOut.model_validate(d)
    elif role == UserRole.PATRON.value:
        if d.statut != "a_valider":
            raise HTTPException(status_code=409, detail="Dossier doit etre 'a_valider' pour validation finale.")
        d.statut = "termine"
    elif role == UserRole.CONSULTANT.value:
        # Cas 2 : le consultant joue le rôle de tous les niveaux
        if d.statut == "en_cours":
            d.statut = "a_valider"
        elif d.statut == "a_valider":
            d.statut = "termine"
        else:
            raise HTTPException(status_code=409, detail=f"Statut '{d.statut}' non validable.")
    else:
        raise HTTPException(status_code=403, detail=f"Role '{role}' non autorise pour cette action.")
    db.commit()
    db.refresh(d)
    return DossierOut.model_validate(d)


@router_dossiers.delete("/{dossier_id}", response_model=MessageOut)
def delete_dossier(dossier_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    d = _find_dossier(db, ctx, dossier_id)
    db.delete(d)
    db.commit()
    return MessageOut(detail="Dossier supprime.")


# =========================================================================
# CAUTIONS BANCAIRES
# =========================================================================
router_cautions = APIRouter(prefix="/cautions", tags=["cautions"])


@router_cautions.get("", response_model=list[CautionOut])
def list_cautions(ctx=Depends(get_current_context), db=Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    rows = db.query(Caution).filter(Caution.entreprise_id == ent.id).all()
    return [CautionOut.model_validate(c) for c in rows]


@router_cautions.post("", response_model=CautionOut, status_code=status.HTTP_201_CREATED)
def create_caution(
    payload: CautionIn, ctx=Depends(get_current_context), db=Depends(get_db)
):
    ent = resolve_entreprise_courante(db, ctx)
    if payload.dossier_id is not None:
        d = db.get(Dossier, payload.dossier_id)
        if d is None or d.entreprise_id != ent.id:
            raise HTTPException(status_code=404, detail="Dossier introuvable.")
    c = Caution(entreprise_id=ent.id, **payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return CautionOut.model_validate(c)


def _find_caution(db, ctx, caution_id) -> Caution:
    ent = resolve_entreprise_courante(db, ctx)
    c = db.get(Caution, caution_id)
    if c is None or c.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="Caution introuvable.")
    return c


@router_cautions.get("/resume", response_model=CautionsResume)
def resume_cautions(ctx=Depends(get_current_context), db=Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    today = date.today()
    rows = (
        db.query(Caution)
        .filter(Caution.entreprise_id == ent.id, Caution.statut == "bloquee")
        .all()
    )
    total = sum(c.montant_da for c in rows)
    par_type: dict[str, int] = {}
    for c in rows:
        par_type[c.type_code] = par_type.get(c.type_code, 0) + c.montant_da

    alertes: list[CautionAlerte] = []
    for c in rows:
        if c.date_recuperation_estimee is None:
            continue
        delta = (c.date_recuperation_estimee - today).days
        if delta > 30:
            continue
        seuil = "expire" if delta < 0 else "7j" if delta <= 7 else "15j" if delta <= 15 else "30j"
        alertes.append(CautionAlerte(
            id=c.id, type_code=c.type_code,
            date_recuperation_estimee=c.date_recuperation_estimee,
            jours_restants=delta, seuil=seuil,
        ))
    alertes.sort(key=lambda a: a.jours_restants)
    return CautionsResume(
        total_bloque_da=total, nombre_actives=len(rows),
        par_type=par_type, alertes=alertes,
    )


@router_cautions.get("/{caution_id}", response_model=CautionOut)
def get_caution(caution_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    return CautionOut.model_validate(_find_caution(db, ctx, caution_id))


@router_cautions.put("/{caution_id}", response_model=CautionOut)
def update_caution(
    caution_id: int, payload: CautionIn,
    ctx=Depends(get_current_context), db=Depends(get_db),
):
    c = _find_caution(db, ctx, caution_id)
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return CautionOut.model_validate(c)


@router_cautions.post("/{caution_id}/recuperer", response_model=CautionOut)
def recuperer_caution(caution_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    c = _find_caution(db, ctx, caution_id)
    c.statut = "recuperee"
    db.commit()
    db.refresh(c)
    return CautionOut.model_validate(c)


@router_cautions.delete("/{caution_id}", response_model=MessageOut)
def delete_caution(caution_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    c = _find_caution(db, ctx, caution_id)
    db.delete(c)
    db.commit()
    return MessageOut(detail="Caution supprimee.")


# =========================================================================
# SOUMISSIONS HISTORIQUE
# =========================================================================
router_soumissions = APIRouter(prefix="/soumissions", tags=["soumissions"])


@router_soumissions.get("", response_model=list[SoumissionOut])
def list_soumissions(ctx=Depends(get_current_context), db=Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    rows = db.query(Soumission).filter(Soumission.entreprise_id == ent.id).all()
    return [SoumissionOut.model_validate(s) for s in rows]


def _compute_ecart(payload: SoumissionIn) -> int | None:
    if payload.montant_soumissionne_da and payload.montant_attributaire_da:
        return int(round(100.0 * (payload.montant_soumissionne_da - payload.montant_attributaire_da)
                         / max(payload.montant_attributaire_da, 1)))
    return None


@router_soumissions.post("", response_model=SoumissionOut, status_code=status.HTTP_201_CREATED)
def create_soumission(
    payload: SoumissionIn, ctx=Depends(get_current_context), db=Depends(get_db)
):
    ent = resolve_entreprise_courante(db, ctx)
    # Verifie ao_id et dossier_id appartiennent a l'entreprise
    if payload.ao_id is not None:
        ao = db.get(AppelOffres, payload.ao_id)
        if ao is None or ao.entreprise_id != ent.id:
            raise HTTPException(status_code=404, detail="AO introuvable.")
    if payload.dossier_id is not None:
        d = db.get(Dossier, payload.dossier_id)
        if d is None or d.entreprise_id != ent.id:
            raise HTTPException(status_code=404, detail="Dossier introuvable.")
    s = Soumission(
        entreprise_id=ent.id,
        **payload.model_dump(),
        ecart_pct=_compute_ecart(payload),
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return SoumissionOut.model_validate(s)


def _find_soum(db, ctx, soum_id) -> Soumission:
    ent = resolve_entreprise_courante(db, ctx)
    s = db.get(Soumission, soum_id)
    if s is None or s.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="Soumission introuvable.")
    return s


@router_soumissions.get("/{soum_id}", response_model=SoumissionOut)
def get_soum(soum_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    return SoumissionOut.model_validate(_find_soum(db, ctx, soum_id))


@router_soumissions.put("/{soum_id}", response_model=SoumissionOut)
def update_soum(soum_id: int, payload: SoumissionIn,
                ctx=Depends(get_current_context), db=Depends(get_db)):
    s = _find_soum(db, ctx, soum_id)
    for k, v in payload.model_dump().items():
        setattr(s, k, v)
    s.ecart_pct = _compute_ecart(payload)
    db.commit()
    db.refresh(s)
    return SoumissionOut.model_validate(s)


@router_soumissions.delete("/{soum_id}", response_model=MessageOut)
def delete_soum(soum_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    s = _find_soum(db, ctx, soum_id)
    db.delete(s)
    db.commit()
    return MessageOut(detail="Soumission supprimee.")
