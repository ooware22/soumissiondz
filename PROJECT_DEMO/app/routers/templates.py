# -*- coding: utf-8 -*-
"""Router /templates — bibliotheque de 5 templates de marches avec chiffrage proportionnel."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_context
from app.models import PrixArticle
from app.schemas import (
    PosteChiffre,
    TemplateChiffreIn,
    TemplateChiffreOut,
    TemplateOut,
)
from app.services.catalogue_seed import TEMPLATES_SEED, seed_prix_articles

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateOut])
def list_templates(_ctx=Depends(get_current_context)):
    return [
        TemplateOut(
            code=t["code"], nom=t["nom"], description=t["description"],
            budget_reference_da=t["budget_reference_da"],
        )
        for t in TEMPLATES_SEED
    ]


@router.post("/{code}/chiffrer", response_model=TemplateChiffreOut)
def chiffrer(
    code: str, payload: TemplateChiffreIn,
    _ctx=Depends(get_current_context), db: Session = Depends(get_db),
):
    tpl = next((t for t in TEMPLATES_SEED if t["code"] == code), None)
    if tpl is None:
        raise HTTPException(status_code=404, detail="Template introuvable.")

    if db.query(PrixArticle).first() is None:
        seed_prix_articles(db)

    # Scale proportionnel des quantites
    ratio = payload.budget_cible_da / tpl["budget_reference_da"]
    article_codes = [p["code"] for p in tpl["postes"]]
    articles = {
        a.code: a for a in db.query(PrixArticle).filter(PrixArticle.code.in_(article_codes)).all()
    }
    missing = [c for c in article_codes if c not in articles]
    if missing:
        raise HTTPException(
            status_code=500, detail=f"Articles de reference manquants: {missing}. Reseed necessaire."
        )

    postes_out: list[PosteChiffre] = []
    total = 0
    for p in tpl["postes"]:
        a = articles[p["code"]]
        q = round(p["quantite"] * ratio, 2)
        t = int(round(q * a.prix_moy_da))
        total += t
        postes_out.append(PosteChiffre(
            article_code=a.code, libelle=a.libelle, unite=a.unite,
            quantite=q, prix_unitaire_da=a.prix_moy_da, total_da=t,
        ))

    return TemplateChiffreOut(
        code=tpl["code"], nom=tpl["nom"],
        budget_cible_da=payload.budget_cible_da,
        montant_calcule_da=total,
        postes=postes_out,
    )
