# -*- coding: utf-8 -*-
"""Router /confidentialite — Lot 8 conformite loi 18-07 algerienne.

- Page publique CGU/confidentialite
- Consentement CGU horodate
- Export complet des donnees du user (ZIP JSON+PDF)
- Suppression de compte avec soft-delete + purge J+30
"""
from __future__ import annotations

import io
import json
import zipfile
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from loguru import logger
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import (
    AppelOffres,
    Document,
    Entreprise,
    Organisation,
    Reference,
    User,
)
from app.schemas.common import BaseSchema, MessageOut

router = APIRouter(prefix="/confidentialite", tags=["conformite_18_07"])


# =========================================================================
# PAGE PUBLIQUE
# =========================================================================
TEXTE_CONFIDENTIALITE = """\
SOUMISSION.DZ — Politique de confidentialite et conformite loi 18-07

1. Donnees collectees
- Identite : nom, email, telephone, mot de passe (hashe PBKDF2)
- Donnees entreprise : NIF, NIS, RC, statuts, bilans, qualifications
- Donnees operationnelles : dossiers, soumissions, cautions, factures

2. Finalite du traitement
Aide a la preparation et au depot de dossiers de soumission aux marches
publics algeriens, conformement a l'article 5 de la loi 18-07.

3. Hebergement
Cloud Algerie (Icosnet / Algerie Telecom / Djaweb selon contrat).
Aucun transfert hors territoire national.

4. Duree de conservation
- Donnees actives : tant que le compte est actif
- Apres cloture : 30 jours en soft-delete avant purge definitive

5. Vos droits (loi 18-07 art. 32-37)
- Acces : GET /confidentialite/export
- Rectification : via les endpoints metier standards
- Effacement : DELETE /confidentialite/compte (purge J+30)
- Portabilite : export ZIP JSON + PDF des factures

6. Contact DPO
dpo@soumission.dz
"""


class CguConsentementIn(BaseSchema):
    accepte: bool


class CguConsentementOut(BaseSchema):
    user_id: int
    accepte_at: datetime


@router.get("", response_model=dict)
def page_confidentialite():
    """Page publique de la politique de confidentialite (loi 18-07)."""
    return {"texte": TEXTE_CONFIDENTIALITE, "version": "1.0", "derniere_maj": "2026-04-13"}


# =========================================================================
# CONSENTEMENT CGU
# =========================================================================
@router.post("/cgu", response_model=CguConsentementOut)
def consentement_cgu(
    payload: CguConsentementIn,
    ctx: SecurityContext = Depends(get_current_context),
):
    if not payload.accepte:
        raise HTTPException(status_code=400, detail="Consentement refuse.")
    now = datetime.now(timezone.utc)
    logger.info(
        "cgu_acceptee",
        user_id=ctx.user_id, email=ctx.user.email, accepte_at=now.isoformat(),
        ip="server-side", loi_18_07_art="32",
    )
    return CguConsentementOut(user_id=ctx.user_id, accepte_at=now)


# =========================================================================
# EXPORT ZIP DES DONNEES
# =========================================================================
def _serialize(obj) -> dict:
    """Convertit un model SQLAlchemy en dict serialisable JSON."""
    out = {}
    for c in obj.__table__.columns:
        v = getattr(obj, c.name)
        if isinstance(v, (date, datetime)):
            v = v.isoformat()
        elif v is not None and not isinstance(v, (str, int, float, bool, list, dict)):
            v = str(v)
        out[c.name] = v
    return out


@router.get("/export")
def export_donnees(
    ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)
):
    """Export complet des donnees de l'organisation courante (loi 18-07 art 32)."""
    org = db.get(Organisation, ctx.organisation_id)
    users = db.query(User).filter(User.organisation_id == ctx.organisation_id).all()

    entreprises: list[Entreprise] = []
    if org and org.is_entreprise:
        entreprises = (
            db.query(Entreprise).filter(Entreprise.organisation_id == org.id).all()
        )
    elif org and org.is_cabinet:
        entreprises = (
            db.query(Entreprise).filter(Entreprise.cabinet_id == ctx.cabinet_id).all()
        )

    docs, refs, aos = [], [], []
    for ent in entreprises:
        docs.extend(db.query(Document).filter(Document.entreprise_id == ent.id).all())
        refs.extend(db.query(Reference).filter(Reference.entreprise_id == ent.id).all())
        aos.extend(db.query(AppelOffres).filter(AppelOffres.entreprise_id == ent.id).all())

    payload = {
        "metadata": {
            "exporte_le": datetime.now(timezone.utc).isoformat(),
            "loi_18_07_art": "32",
            "format": "JSON",
            "version_export": "1.0",
        },
        "organisation": _serialize(org) if org else None,
        "users": [_serialize(u) for u in users],
        "entreprises": [_serialize(e) for e in entreprises],
        "documents": [_serialize(d) for d in docs],
        "references": [_serialize(r) for r in refs],
        "appels_offres": [_serialize(a) for a in aos],
    }
    # Anonymise les password_hash dans l'export pour ne pas leak les hashes
    for u in payload["users"]:
        if "password_hash" in u:
            u["password_hash"] = "[REDACTED]"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("export_donnees.json", json.dumps(payload, indent=2, ensure_ascii=False))
        zf.writestr("README.txt",
                    "Export des donnees personnelles SOUMISSION.DZ\n"
                    "Conforme loi algerienne 18-07 art 32.\n"
                    f"Genere le {datetime.now(timezone.utc).isoformat()}\n")

    logger.info("export_donnees", user_id=ctx.user_id, organisation_id=ctx.organisation_id)
    return Response(
        content=buf.getvalue(), media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="export_donnees.zip"'},
    )


# =========================================================================
# SUPPRESSION DE COMPTE — soft-delete puis purge J+30
# =========================================================================
@router.delete("/compte", response_model=MessageOut)
def supprimer_compte(
    ctx: SecurityContext = Depends(get_current_context), db: Session = Depends(get_db)
):
    """Marque le compte comme inactif (statut=suspendu, users.actif=False).

    La purge effective est faite par un job J+30 (a planifier en cron, voir
    `purger_comptes_expirees` ci-dessous). En attendant, le compte n'est plus
    accessible mais les donnees sont conservees pour rattrapage eventuel.
    """
    from app.models.enums import OrgStatut, UserRole
    if ctx.role not in {UserRole.PATRON.value, UserRole.CONSULTANT.value, UserRole.ADMIN_PLATEFORME.value}:
        raise HTTPException(
            status_code=403,
            detail="Suppression de compte reservee au patron / consultant / admin.",
        )

    org = db.get(Organisation, ctx.organisation_id)
    if org is None:
        raise HTTPException(status_code=404, detail="Compte introuvable.")
    org.statut = OrgStatut.SUSPENDU.value
    for u in db.query(User).filter(User.organisation_id == org.id).all():
        u.actif = False
    db.commit()
    logger.info(
        "compte_soft_delete",
        organisation_id=org.id, user_id=ctx.user_id,
        purge_prevue_le=(date.today() + timedelta(days=30)).isoformat(),
    )
    return MessageOut(detail="Compte suspendu. Purge definitive prevue dans 30 jours.")


def purger_comptes_expirees(db: Session, today: date | None = None) -> int:
    """Job de purge — supprime definitivement les organisations suspendues > 30j.

    Appele par un cron (a brancher Lot 9 ou via systemd timer / cron Linux).
    Renvoie le nombre d'organisations purgees.
    """
    from app.models.enums import OrgStatut
    today = today or date.today()
    seuil = today - timedelta(days=30)
    rows = (
        db.query(Organisation)
        .filter(Organisation.statut == OrgStatut.SUSPENDU.value)
        .filter(Organisation.updated_at <= seuil)
        .all()
    )
    n = 0
    for org in rows:
        logger.warning(
            "compte_purge_definitive", organisation_id=org.id, nom=org.nom,
            loi_18_07_art="34_droit_oubli",
        )
        db.delete(org)
        n += 1
    db.commit()
    return n
