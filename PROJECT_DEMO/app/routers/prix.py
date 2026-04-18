# -*- coding: utf-8 -*-
"""Router /prix — catalogue 35 articles BTPH + simulateur."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_context
from app.models import PrixArticle
from app.schemas import (
    PosteSimule,
    PrixArticleOut,
    SimulationIn,
    SimulationOut,
)
from app.services.catalogue_seed import seed_prix_articles

router = APIRouter(prefix="/prix", tags=["prix"])


@router.get("/articles", response_model=list[PrixArticleOut])
def list_articles(_ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    # Idempotent : seed a la demande si table vide (utile en dev + tests)
    if db.query(PrixArticle).first() is None:
        seed_prix_articles(db)
    articles = db.query(PrixArticle).order_by(PrixArticle.categorie, PrixArticle.code).all()
    return [PrixArticleOut.model_validate(a) for a in articles]


@router.post("/simuler", response_model=SimulationOut)
def simuler(
    payload: SimulationIn, _ctx=Depends(get_current_context), db: Session = Depends(get_db)
):
    if db.query(PrixArticle).first() is None:
        seed_prix_articles(db)
    codes = [p.article_code for p in payload.postes]
    articles = {
        a.code: a for a in db.query(PrixArticle).filter(PrixArticle.code.in_(codes)).all()
    }
    missing = [c for c in codes if c not in articles]
    if missing:
        raise HTTPException(status_code=422, detail=f"Articles inconnus: {missing}")

    postes_out: list[PosteSimule] = []
    total_prop = 0
    total_ref = 0
    for p in payload.postes:
        a = articles[p.article_code]
        total_prop += int(p.prix_propose_da * p.quantite)
        total_ref += int(a.prix_moy_da * p.quantite)
        ecart = 100.0 * (p.prix_propose_da - a.prix_moy_da) / max(a.prix_moy_da, 1)
        if p.prix_propose_da < a.prix_min_da or p.prix_propose_da > a.prix_max_da:
            verdict = "hors_fourchette"
        elif ecart < -10:
            verdict = "bas"
        elif ecart > 10:
            verdict = "haut"
        else:
            verdict = "ok"
        postes_out.append(PosteSimule(
            article_code=a.code, libelle=a.libelle,
            quantite=p.quantite, prix_propose_da=p.prix_propose_da,
            prix_moy_da=a.prix_moy_da, ecart_vs_moy_pct=round(ecart, 2),
            verdict=verdict,
        ))
    ecart_global = 100.0 * (total_prop - total_ref) / max(total_ref, 1)
    return SimulationOut(
        postes=postes_out,
        montant_total_propose_da=total_prop,
        montant_total_reference_da=total_ref,
        ecart_global_pct=round(ecart_global, 2),
    )
