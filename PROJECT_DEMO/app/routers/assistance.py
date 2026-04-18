# -*- coding: utf-8 -*-
"""Router /assistance — Cas 3 complet : catalogue, missions, mandats, assistants, messagerie."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import SecurityContext, get_current_context
from app.models import (
    AoMandatAction,
    AssistantAgree,
    Mandat,
    Mission,
    MissionMessage,
    PrestationCatalogue,
    User,
)
from app.models.enums import UserRole
from app.models.phase4 import PRESTATIONS_SEED
from app.schemas import (
    ActionMandatOut,
    AssistantOut,
    MandatOut,
    MandatSignatureIn,
    MessageIn,
    MessageOut2,
    MessageOut,
    MissionContestationIn,
    MissionDemandeIn,
    MissionLivraisonIn,
    MissionOut,
    MissionValidationIn,
    PrestationOut,
)
from app.scoping import resolve_entreprise_courante


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _seed_prestations(db: Session) -> None:
    if db.query(PrestationCatalogue).first():
        return
    for code, nom, desc, prix, delai in PRESTATIONS_SEED:
        db.add(PrestationCatalogue(
            code=code, nom=nom, description=desc,
            prix_ht_da=prix, delai_max_jours=delai, actif=True,
        ))
    db.commit()


# =========================================================================
# CATALOGUE PUBLIC (consultable par tout user authentifie)
# =========================================================================
router_catalogue = APIRouter(prefix="/assistance/prestations", tags=["assistance"])


@router_catalogue.get("", response_model=list[PrestationOut])
def list_prestations(_ctx=Depends(get_current_context), db: Session = Depends(get_db)):
    _seed_prestations(db)
    items = (
        db.query(PrestationCatalogue)
        .filter(PrestationCatalogue.actif == True)  # noqa: E712
        .order_by(PrestationCatalogue.prix_ht_da)
        .all()
    )
    return [PrestationOut.model_validate(p) for p in items]


# =========================================================================
# MISSIONS — cycle de vie complet
# =========================================================================
router_missions = APIRouter(prefix="/missions", tags=["missions"])


def _affecter_assistant(db: Session, mission: Mission) -> AssistantAgree | None:
    """Algorithme par defaut : premier assistant agree actif disponible."""
    return (
        db.query(AssistantAgree)
        .filter(AssistantAgree.actif == True)  # noqa: E712
        .order_by(AssistantAgree.note_moyenne.desc(), AssistantAgree.id)
        .first()
    )


@router_missions.post("", response_model=MissionOut, status_code=status.HTTP_201_CREATED)
def demander_mission(
    payload: MissionDemandeIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Etape 1 — Le client decrit la mission. Statut 'brouillon'."""
    _seed_prestations(db)
    ent = resolve_entreprise_courante(db, ctx)
    prest = (
        db.query(PrestationCatalogue)
        .filter(PrestationCatalogue.code == payload.prestation_code)
        .one_or_none()
    )
    if prest is None:
        raise HTTPException(status_code=404, detail="Prestation inconnue.")

    prix_ttc = int(round(prest.prix_ht_da * 1.19))
    m = Mission(
        entreprise_id=ent.id, prestation_id=prest.id, ao_id=payload.ao_id,
        brief=payload.brief, statut="brouillon",
        prix_ht_da=prest.prix_ht_da, tva=19, prix_ttc_da=prix_ttc,
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return MissionOut.model_validate(m)


@router_missions.get("", response_model=list[MissionOut])
def list_missions(ctx=Depends(get_current_context), db=Depends(get_db)):
    ent = resolve_entreprise_courante(db, ctx)
    rows = db.query(Mission).filter(Mission.entreprise_id == ent.id).all()
    return [MissionOut.model_validate(m) for m in rows]


def _find_mission(db: Session, ctx: SecurityContext, mission_id: int) -> Mission:
    ent = resolve_entreprise_courante(db, ctx)
    m = db.get(Mission, mission_id)
    if m is None or m.entreprise_id != ent.id:
        raise HTTPException(status_code=404, detail="Mission introuvable.")
    return m


@router_missions.get("/{mission_id}", response_model=MissionOut)
def get_mission(mission_id: int, ctx=Depends(get_current_context), db=Depends(get_db)):
    return MissionOut.model_validate(_find_mission(db, ctx, mission_id))


@router_missions.post("/{mission_id}/signer-mandat", response_model=MandatOut)
def signer_mandat(
    mission_id: int,
    payload: MandatSignatureIn,
    request: Request,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Etape 2 — Le client signe electroniquement le mandat. Affecte un assistant."""
    if not payload.accepte:
        raise HTTPException(status_code=400, detail="Le mandat doit etre accepte pour proceder.")
    mission = _find_mission(db, ctx, mission_id)
    if mission.statut != "brouillon":
        raise HTTPException(status_code=409, detail=f"Mission deja au statut '{mission.statut}'.")

    today = date.today()
    mandat = Mandat(
        entreprise_id=mission.entreprise_id, mission_id=mission.id,
        signe_at=_utcnow(),
        signe_ip=request.client.host if request.client else None,
        signe_user_agent=request.headers.get("user-agent"),
        valide_du=today,
        valide_jusqu_au=today + timedelta(days=payload.valide_jours),
        perimetre_actions=["lecture_dossier", "modification_dossier", "upload_documents", "depot"],
        statut="signe",
    )
    db.add(mandat)
    db.flush()

    # Affectation auto
    asst = _affecter_assistant(db, mission)
    if asst:
        mandat.assistant_id = asst.id
        mission.assistant_id = asst.id
        mission.affectee_at = _utcnow()
        mission.statut = "en_cours"
        mission.demarree_at = _utcnow()
    else:
        mission.statut = "paiement_attendu"

    db.commit()
    db.refresh(mandat)
    return MandatOut.model_validate(mandat)


@router_missions.post("/{mission_id}/livrer", response_model=MissionOut)
def livrer_mission(
    mission_id: int, payload: MissionLivraisonIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Etape 7 — L'assistant declare la mission terminee.

    Securite : seul un assistant agree peut declarer la livraison, ET il doit
    etre celui affecte a la mission, ET un mandat valide doit exister.
    """
    if ctx.role != UserRole.ASSISTANT_AGREE.value:
        raise HTTPException(status_code=403, detail="Action reservee aux assistants agrees.")

    asst = (
        db.query(AssistantAgree).filter(AssistantAgree.user_id == ctx.user_id).one_or_none()
    )
    if asst is None:
        raise HTTPException(status_code=403, detail="Profil assistant introuvable.")

    mission = db.get(Mission, mission_id)
    if mission is None or mission.assistant_id != asst.id:
        raise HTTPException(status_code=404, detail="Mission introuvable.")
    if mission.statut != "en_cours":
        raise HTTPException(status_code=409, detail=f"Statut '{mission.statut}' non livrable.")

    # Mandat en vigueur ?
    today = date.today()
    mandat = (
        db.query(Mandat)
        .filter(
            Mandat.mission_id == mission.id,
            Mandat.assistant_id == asst.id,
            Mandat.statut == "signe",
        )
        .one_or_none()
    )
    if mandat is None or mandat.valide_jusqu_au is None or mandat.valide_jusqu_au < today:
        raise HTTPException(status_code=403, detail="Mandat absent, expire ou invalide.")

    mission.livrables = payload.livrables
    mission.livree_at = _utcnow()
    mission.statut = "livree"

    # Journal d'action
    db.add(AoMandatAction(
        mandat_id=mandat.id, user_id_assistant=ctx.user_id,
        action_type="livraison_mission",
        action_payload={"livrables": payload.livrables, "mission_id": mission.id},
    ))
    db.commit()
    db.refresh(mission)
    return MissionOut.model_validate(mission)


@router_missions.post("/{mission_id}/valider", response_model=MissionOut)
def valider_mission(
    mission_id: int, payload: MissionValidationIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Etape 8 — Le client valide la livraison (sous 48h sinon auto)."""
    mission = _find_mission(db, ctx, mission_id)
    if mission.statut != "livree":
        raise HTTPException(status_code=409, detail="Mission pas en statut 'livree'.")
    mission.statut = "validee"
    mission.validee_at = _utcnow()
    mission.note_client = payload.note
    mission.commentaire_client = payload.commentaire

    # Met a jour la note moyenne de l'assistant
    if mission.assistant_id:
        asst = db.get(AssistantAgree, mission.assistant_id)
        if asst:
            n = asst.nb_missions_terminees
            new_n = n + 1
            new_note = int(round((asst.note_moyenne * n + payload.note * 20) / new_n))
            asst.note_moyenne = new_note
            asst.nb_missions_terminees = new_n
    db.commit()
    db.refresh(mission)
    return MissionOut.model_validate(mission)


@router_missions.post("/{mission_id}/contester", response_model=MissionOut)
def contester_mission(
    mission_id: int, payload: MissionContestationIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Le client conteste une livraison. Statut -> 'contestee', resolution manuelle."""
    mission = _find_mission(db, ctx, mission_id)
    if mission.statut != "livree":
        raise HTTPException(status_code=409, detail="Mission pas en statut 'livree'.")
    mission.statut = "contestee"
    mission.commentaire_client = f"[CONTESTATION] {payload.motif}"
    db.commit()
    db.refresh(mission)
    return MissionOut.model_validate(mission)


# =========================================================================
# JOURNAL D'ACTIONS DU MANDAT (lecture client)
# =========================================================================
router_mandat_journal = APIRouter(prefix="/missions/{mission_id}/journal", tags=["missions"])


@router_mandat_journal.get("", response_model=list[ActionMandatOut])
def journal_mandat(
    mission_id: int,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    """Le client consulte la trace de toutes les actions effectuees par l'assistant."""
    mission = _find_mission(db, ctx, mission_id)
    mandats = db.query(Mandat).filter(Mandat.mission_id == mission.id).all()
    if not mandats:
        return []
    mandat_ids = [m.id for m in mandats]
    actions = (
        db.query(AoMandatAction)
        .filter(AoMandatAction.mandat_id.in_(mandat_ids))
        .order_by(AoMandatAction.created_at)
        .all()
    )
    return [ActionMandatOut.model_validate(a) for a in actions]


# =========================================================================
# MESSAGERIE MISSION (client <-> assistant)
# =========================================================================
router_messages = APIRouter(prefix="/missions/{mission_id}/messages", tags=["missions"])


def _verifier_acces_message(db: Session, ctx: SecurityContext, mission_id: int) -> tuple[Mission, str]:
    """Renvoie (mission, role_auteur). Le client OU l'assistant affecte ont acces."""
    mission = db.get(Mission, mission_id)
    if mission is None:
        raise HTTPException(status_code=404, detail="Mission introuvable.")

    # Cas client
    if ctx.organisation_type in ("entreprise", "cabinet"):
        try:
            ent = resolve_entreprise_courante(db, ctx)
            if mission.entreprise_id == ent.id:
                return mission, "client"
        except HTTPException:
            pass

    # Cas assistant agree
    if ctx.role == UserRole.ASSISTANT_AGREE.value:
        asst = (
            db.query(AssistantAgree).filter(AssistantAgree.user_id == ctx.user_id).one_or_none()
        )
        if asst and mission.assistant_id == asst.id:
            return mission, "assistant"

    raise HTTPException(status_code=404, detail="Mission introuvable.")


@router_messages.get("", response_model=list[MessageOut2])
def list_messages(
    mission_id: int,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    mission, _ = _verifier_acces_message(db, ctx, mission_id)
    rows = (
        db.query(MissionMessage)
        .filter(MissionMessage.mission_id == mission.id)
        .order_by(MissionMessage.created_at)
        .all()
    )
    return [MessageOut2.model_validate(m) for m in rows]


@router_messages.post("", response_model=MessageOut2, status_code=status.HTTP_201_CREATED)
def post_message(
    mission_id: int, payload: MessageIn,
    ctx: SecurityContext = Depends(get_current_context),
    db: Session = Depends(get_db),
):
    mission, role = _verifier_acces_message(db, ctx, mission_id)
    msg = MissionMessage(
        mission_id=mission.id, auteur_user_id=ctx.user_id,
        role_auteur=role, message=payload.message,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return MessageOut2.model_validate(msg)
