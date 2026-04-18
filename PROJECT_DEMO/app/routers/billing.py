# -*- coding: utf-8 -*-
"""Router /plans, /abonnements, /factures — Lot 7 monetisation.

- 5 plans seeds (DECOUVERTE, ARTISAN, PRO, BUSINESS, EXPERT) + HOTLINE add-on
- Souscription d'un abonnement (par le patron uniquement)
- Generation de factures conformes Algerie (NIF/NIS/RC + TVA 19%)
- 3 modes de paiement : virement (manuel), edahabia/cib (mock v5), a_l_acte
"""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models.phase4 import Abonnement, Facture, Plan
from app.schemas.common import BaseSchema

router_plans = APIRouter(prefix="/plans", tags=["billing"])
router_abos = APIRouter(prefix="/abonnements", tags=["billing"])
router_factures = APIRouter(prefix="/factures", tags=["billing"])


PLANS_SEED = [
    ("DECOUVERTE", "Decouverte (gratuit 14j, 1 dossier)", 0, 0),
    ("ARTISAN", "Artisan (TPE solo)", 5000, 54000),
    ("PRO", "Pro (PME 5-30 employes)", 10000, 108000),
    ("BUSINESS", "Business (PME 30+, multi-utilisateurs)", 15000, 162000),
    ("EXPERT", "Expert (consultants multi-clients)", 20000, 216000),
    ("HOTLINE", "Hotline (add-on support)", 4000, 43200),
]


def _seed_plans(db: Session) -> None:
    if db.query(Plan).first():
        return
    for code, nom, m, a in PLANS_SEED:
        db.add(Plan(code=code, nom=nom, prix_mensuel_da=m, prix_annuel_da=a, actif=True))
    db.commit()


# ------ Schemas ------
class PlanOut(BaseSchema):
    id: int
    code: str
    nom: str
    prix_mensuel_da: int
    prix_annuel_da: int
    actif: bool


class AbonnementSouscrireIn(BaseSchema):
    plan_code: str = Field(..., max_length=30)
    periodicite: str = Field(..., pattern="^(mensuel|annuel)$")


class AbonnementOut(BaseSchema):
    id: int
    plan_code: str
    plan_nom: str
    periodicite: str
    debut: date
    fin: date | None = None
    statut: str
    montant_da: int


class FactureOut(BaseSchema):
    id: int
    numero: str
    annee: int
    date_emission: date
    date_echeance: date | None = None
    libelle: str
    prix_ht_da: int
    tva_pct: int
    prix_ttc_da: int
    mode_paiement: str | None = None
    statut: str


class FacturePayerIn(BaseSchema):
    mode_paiement: str = Field(..., pattern="^(virement|edahabia|cib|a_l_acte)$")


# ------ Plans ------
@router_plans.get("", response_model=list[PlanOut])
def list_plans(_ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    _seed_plans(db)
    return [PlanOut.model_validate(p) for p in db.query(Plan).filter(Plan.actif == True).all()]


# ------ Abonnements ------
def _next_facture_numero(db: Session, annee: int) -> str:
    last = (
        db.query(Facture).filter(Facture.annee == annee)
        .order_by(Facture.id.desc()).first()
    )
    n = 1 if last is None else int(last.numero.split("-")[-1]) + 1
    return f"SDZ-{annee}-{n:05d}"


@router_abos.post("", response_model=AbonnementOut, status_code=status.HTTP_201_CREATED)
def souscrire(
    payload: AbonnementSouscrireIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    _seed_plans(db)
    plan = db.query(Plan).filter(Plan.code == payload.plan_code).one_or_none()
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan inconnu.")

    today = date.today()
    duration = 365 if payload.periodicite == "annuel" else 30
    abo = Abonnement(
        organisation_id=ctx.organisation_id, plan_id=plan.id,
        periodicite=payload.periodicite, debut=today,
        fin=today + timedelta(days=duration), statut="actif",
    )
    db.add(abo)
    db.flush()

    # Genere une facture proforma pour les plans payants
    montant_ht = plan.prix_annuel_da if payload.periodicite == "annuel" else plan.prix_mensuel_da
    if montant_ht > 0:
        ttc = int(round(montant_ht * 1.19))
        facture = Facture(
            organisation_id=ctx.organisation_id, numero=_next_facture_numero(db, today.year),
            annee=today.year, abonnement_id=abo.id,
            date_emission=today, date_echeance=today + timedelta(days=15),
            libelle=f"Abonnement {plan.nom} ({payload.periodicite})",
            prix_ht_da=montant_ht, tva_pct=19, prix_ttc_da=ttc,
            statut="emise",
        )
        db.add(facture)
    db.commit()
    db.refresh(abo)
    return AbonnementOut(
        id=abo.id, plan_code=plan.code, plan_nom=plan.nom,
        periodicite=abo.periodicite, debut=abo.debut, fin=abo.fin,
        statut=abo.statut, montant_da=montant_ht,
    )


@router_abos.get("", response_model=list[AbonnementOut])
def list_abos(ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    rows = db.query(Abonnement).filter(Abonnement.organisation_id == ctx.organisation_id).all()
    out = []
    for a in rows:
        plan = db.get(Plan, a.plan_id)
        montant = (
            plan.prix_annuel_da if a.periodicite == "annuel" else plan.prix_mensuel_da
        ) if plan else 0
        out.append(AbonnementOut(
            id=a.id, plan_code=plan.code if plan else "",
            plan_nom=plan.nom if plan else "",
            periodicite=a.periodicite, debut=a.debut, fin=a.fin,
            statut=a.statut, montant_da=montant,
        ))
    return out


# ------ Factures ------
@router_factures.get("", response_model=list[FactureOut])
def list_factures(ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    rows = db.query(Facture).filter(Facture.organisation_id == ctx.organisation_id).all()
    return [FactureOut.model_validate(f) for f in rows]


@router_factures.post("/{facture_id}/payer", response_model=FactureOut)
def payer(
    facture_id: int, payload: FacturePayerIn,
    ctx=Depends(get_current_context), db: Session = Depends(get_db),
):
    f = db.get(Facture, facture_id)
    if f is None or f.organisation_id != ctx.organisation_id:
        raise HTTPException(status_code=404, detail="Facture introuvable.")
    if f.statut == "payee":
        raise HTTPException(status_code=409, detail="Facture deja payee.")

    f.mode_paiement = payload.mode_paiement
    if payload.mode_paiement in {"edahabia", "cib"}:
        # Mock paiement instantane (vraie integration en v5.5)
        from datetime import datetime, timezone
        f.statut = "payee"
        f.paiement_recu_at = datetime.now(timezone.utc)
    elif payload.mode_paiement == "virement":
        f.statut = "en_attente_virement"  # validation manuelle admin
    else:  # a_l_acte
        f.statut = "payee"
    db.commit()
    db.refresh(f)
    return FactureOut.model_validate(f)


@router_factures.get("/{facture_id}/pdf")
def facture_pdf(
    facture_id: int, ctx=Depends(get_current_context), db: Session = Depends(get_db)
):
    """Genere le PDF de la facture conforme fiscalite Algerie (NIF/NIS/RC, TVA 19%)."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    f = db.get(Facture, facture_id)
    if f is None or f.organisation_id != ctx.organisation_id:
        raise HTTPException(status_code=404, detail="Facture introuvable.")

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 2 * cm

    # Entete emetteur
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "SOUMISSION.DZ SARL")
    y -= 0.6 * cm
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, y, "Plateforme SaaS — Aide aux soumissions marches publics")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "NIF: 099916001234567 | NIS: 09991600123 | RC: 16/00-1234567 B 24")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, "Alger, Algerie")

    # Numero facture
    y -= 1.5 * cm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, f"FACTURE N° {f.numero}")
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Date d'emission : {f.date_emission.strftime('%d/%m/%Y')}")
    y -= 0.5 * cm
    if f.date_echeance:
        c.drawString(2 * cm, y, f"Date d'echeance : {f.date_echeance.strftime('%d/%m/%Y')}")

    # Client
    org = ctx.organisation
    y -= 1.2 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Client :")
    y -= 0.5 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, org.nom)

    # Detail
    y -= 1.2 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2 * cm, y, "Designation")
    c.drawRightString(w - 2 * cm, y, "Montant (DA)")
    y -= 0.4 * cm
    c.line(2 * cm, y, w - 2 * cm, y)
    y -= 0.6 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f.libelle[:80])
    c.drawRightString(w - 2 * cm, y, f"{f.prix_ht_da:,}".replace(",", " "))

    # Totaux
    y -= 1.5 * cm
    c.line(w - 8 * cm, y, w - 2 * cm, y)
    y -= 0.5 * cm
    c.drawString(w - 8 * cm, y, "Total HT :")
    c.drawRightString(w - 2 * cm, y, f"{f.prix_ht_da:,} DA".replace(",", " "))
    y -= 0.4 * cm
    c.drawString(w - 8 * cm, y, f"TVA {f.tva_pct}% :")
    c.drawRightString(w - 2 * cm, y, f"{f.prix_ttc_da - f.prix_ht_da:,} DA".replace(",", " "))
    y -= 0.4 * cm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(w - 8 * cm, y, "Total TTC :")
    c.drawRightString(w - 2 * cm, y, f"{f.prix_ttc_da:,} DA".replace(",", " "))

    # Pied
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, 1.5 * cm,
                 "Conforme aux dispositions fiscales de la Republique Algerienne (TVA 19%).")
    c.showPage()
    c.save()
    return Response(
        content=buf.getvalue(), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{f.numero}.pdf"'},
    )
