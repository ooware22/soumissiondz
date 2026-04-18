# -*- coding: utf-8 -*-
"""Seeds de demonstration — plateforme simulee apres 2 mois d'exploitation.

Cree un etat de base credible pour une demo commerciale :

  - 1 admin plateforme (admin@soumission.dz / Admin12345)
  - 5 entreprises Cas 1 + 1 cabinet Cas 2 avec 3 entreprises dans son portefeuille
    = 8 entites entreprise au total, 6 comptes clients distincts
  - 2 assistants agrees Cas 3 (Yacine BTPH+VRD, Samira fournitures+services)
  - Catalogue 35 articles BTPH + 5 templates + 7 prestations + 6 plans seeds
  - Pour chaque entreprise :
      * Coffre-fort rempli (15 types officiels, dates d'expiration variees
        pour generer des alertes 7j/15j/30j credibles)
      * 3 a 6 references de marches historiques
      * Abonnement SOUMISSION.DZ actif (ARTISAN/PRO/BUSINESS/EXPERT selon taille)
      * Factures emises + payees sur 2 mois
  - 20 AO repartis sur les 2 derniers mois :
      * 12 gagnes (60%), 6 perdus, 2 en cours
      * Chaque gagne : dossier complet + caution soumission 1% + caution
        bonne execution 5% si demarre + ligne de soumission avec rang et
        ecart attributaire
  - 4 missions Cas 3 dans des etats varies (brouillon, en_cours, validee, contestee)
      * Messagerie client<->assistant avec plusieurs echanges
      * Journal d'actions du mandat
  - 8 tickets hotline (niveaux varies, certains resolus)
  - Codes de parrainage generes + 3 commissions de parrainage mensuelles
  - Cautions bancaires : mix actives (BNA/CPA/BDL/BEA) + alertes d'expiration

Lancement : python -m app.seeds_demo  (idempotent)
"""
from __future__ import annotations

import random
import secrets
import sys
from datetime import date, datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import (
    AppelOffres,
    Cabinet,
    Document,
    Entreprise,
    Organisation,
    Reference,
    User,
)
from app.models.dossier import Caution, Dossier, Soumission
from app.models.enums import OrgStatut, OrgType, PlanCode, UserRole
from app.models.phase4 import (
    Abonnement,
    AoMandatAction,
    AssistantAgree,
    CodeParrainage,
    Commission,
    Facture,
    Mandat,
    Mission,
    MissionMessage,
    Plan,
    PrestationCatalogue,
    TicketHotline,
)
from app.security import hash_password
from app.services.catalogue_seed import seed_prix_articles

# Reproductibilite : meme seeds = meme scenario
random.seed(20260413)


def log(msg: str) -> None:
    print(f"[seeds] {msg}")


TODAY = date.today()
# La plateforme fait croire qu'elle tourne depuis 2 mois
J_MINUS_60 = TODAY - timedelta(days=60)


# =============================================================================
# CATALOGUE : 6 clients, dont 5 entreprises autonomes + 1 cabinet (3 entreprises)
# =============================================================================

ENTREPRISES_CAS1 = [
    {
        "email": "brahim@alpha-btph.dz", "patron": "brahim", "patron_nom": "Brahim Mansouri",
        "nom": "Alpha BTPH", "forme_juridique": "SARL",
        "wilaya_code": "22", "wilaya_nom": "Sidi Bel Abbes",
        "nif": "099922001234567", "nis": "09992200123",
        "rc": "22/00-1234567 B 18", "gerant": "Brahim Mansouri",
        "telephone": "+213 48 51 23 45", "secteur": "BTPH",
        "activite": "Travaux publics, voirie, batiments",
        "effectif": 35, "ca_moyen_da": 180_000_000,
        "qualification_cat": "IV",
        "qualification_expiration": date(2027, 6, 30),
        "adresse": "Zone industrielle, Sidi Bel Abbes",
        "plan": PlanCode.PRO.value,
    },
    {
        "email": "kamel@batipro-setif.dz", "patron": "kamel", "patron_nom": "Kamel Boudiaf",
        "nom": "Batipro Setif", "forme_juridique": "SARL",
        "wilaya_code": "19", "wilaya_nom": "Setif",
        "nif": "099919001345678", "nis": "09991900134",
        "rc": "19/00-2345678 B 16", "gerant": "Kamel Boudiaf",
        "telephone": "+213 36 84 12 34", "secteur": "BTPH",
        "activite": "Construction batiments publics et logements LPP",
        "effectif": 85, "ca_moyen_da": 420_000_000,
        "qualification_cat": "VI",
        "qualification_expiration": date(2026, 12, 31),
        "adresse": "Cite Tlidjene, Setif",
        "plan": PlanCode.BUSINESS.value,
    },
    {
        "email": "amine@hydra-etudes.dz", "patron": "amine", "patron_nom": "Amine Belhadi",
        "nom": "Hydra Etudes", "forme_juridique": "EURL",
        "wilaya_code": "16", "wilaya_nom": "Alger",
        "nif": "099916001456789", "nis": "09991600145",
        "rc": "16/00-3456789 B 20", "gerant": "Amine Belhadi",
        "telephone": "+213 23 75 12 34", "secteur": "Etudes",
        "activite": "Bureau d'etudes hydraulique et VRD",
        "effectif": 12, "ca_moyen_da": 65_000_000,
        "qualification_cat": "III",
        "qualification_expiration": date(2027, 3, 15),
        "adresse": "Hydra, Alger",
        "plan": PlanCode.PRO.value,
    },
    {
        "email": "nadia@omega-fournitures.dz", "patron": "nadia", "patron_nom": "Nadia Cherif",
        "nom": "Omega Fournitures", "forme_juridique": "SARL",
        "wilaya_code": "31", "wilaya_nom": "Oran",
        "nif": "099931001567890", "nis": "09993100156",
        "rc": "31/00-4567890 B 19", "gerant": "Nadia Cherif",
        "telephone": "+213 41 33 22 11", "secteur": "Fournitures",
        "activite": "Importation et distribution materiel medical et bureau",
        "effectif": 18, "ca_moyen_da": 95_000_000,
        "adresse": "Boulevard de l'ALN, Oran",
        "plan": PlanCode.PRO.value,
    },
    {
        "email": "omar@sud-travaux.dz", "patron": "omar", "patron_nom": "Omar Belkacem",
        "nom": "Sud Travaux Ghardaia", "forme_juridique": "EURL",
        "wilaya_code": "47", "wilaya_nom": "Ghardaia",
        "nif": "099947001678901", "nis": "09994700167",
        "rc": "47/00-5678901 B 22", "gerant": "Omar Belkacem",
        "telephone": "+213 29 87 65 43", "secteur": "Services",
        "activite": "Travaux divers, services aux administrations",
        "effectif": 8, "ca_moyen_da": 28_000_000,
        "adresse": "Centre-ville, Ghardaia",
        "plan": PlanCode.ARTISAN.value,
    },
]

# 3 entreprises sous gestion du cabinet Mourad
ENTREPRISES_PORTEFEUILLE_MOURAD = [
    {
        "nom": "BatiWilaya Blida", "forme_juridique": "SARL",
        "wilaya_code": "09", "wilaya_nom": "Blida",
        "nif": "099909001123456", "nis": "09990900112",
        "rc": "09/00-1123456 B 21", "gerant": "Rachid Bouchelaghem",
        "telephone": "+213 25 40 11 22", "secteur": "BTPH",
        "activite": "Gros oeuvre et second oeuvre batiment",
        "effectif": 22, "ca_moyen_da": 115_000_000,
        "qualification_cat": "III",
        "qualification_expiration": date(2027, 4, 20),
        "email": "contact@batiwilaya.dz",
    },
    {
        "nom": "ElectroBourouba", "forme_juridique": "SARL",
        "wilaya_code": "16", "wilaya_nom": "Alger",
        "nif": "099916001234511", "nis": "09991600123",
        "rc": "16/00-4321098 B 19", "gerant": "Tarek Khelifi",
        "telephone": "+213 23 77 55 66", "secteur": "Electricite",
        "activite": "Installations electriques basse et moyenne tension",
        "effectif": 14, "ca_moyen_da": 58_000_000,
        "qualification_cat": "III",
        "qualification_expiration": date(2026, 11, 10),
        "email": "contact@electrobourouba.dz",
    },
    {
        "nom": "AgroFournis Annaba", "forme_juridique": "EURL",
        "wilaya_code": "23", "wilaya_nom": "Annaba",
        "nif": "099923001445566", "nis": "09992300144",
        "rc": "23/00-5544332 B 23", "gerant": "Lotfi Djebbar",
        "telephone": "+213 38 86 11 33", "secteur": "Fournitures",
        "activite": "Fournitures agricoles et d'elevage",
        "effectif": 9, "ca_moyen_da": 42_000_000,
        "email": "contact@agrofournis.dz",
    },
]


# =============================================================================
# 15 types documents officiels — seeds les 10 les plus courants par entreprise
# avec dates d'expiration variees (10 a 180 jours)
# =============================================================================

DOCS_PAR_ENTREPRISE = [
    ("CNAS", 90),          # Expire dans 90j
    ("CASNOS", 45),        # 45j
    ("CACOBATPH", 180),    # 180j (BTPH uniquement, on filtrera)
    ("NIF", None),         # sans expiration
    ("NIS", None),
    ("RC", None),
    ("EXTRAIT_ROLE", 30),  # 30j — borderline alerte
    ("ATTESTATION_FISCALE", 15),  # 15j — ALERTE
    ("STATUTS", None),
    ("CASIER_JUDICIAIRE", 80),
    ("BILAN_2023", None),
    ("BILAN_2024", None),
    ("QUALIFICATION_BTPH", 240),  # BTPH uniquement
    ("ATTESTATION_BANCAIRE", 6),  # 6j — ALERTE URGENCE
]


# =============================================================================
# 20 appels d'offres realistes — mix travaux/fournitures/services, wilayas variees
# =============================================================================

AO_TEMPLATE = [
    # (objet, MO, wilaya_code, budget_da, qualification_cat, activites, delai_offset_debut)
    # Gagnes (12 premiers)
    ("Refection chaussee RN13 sur 5 km", "Direction des Travaux Publics SBA", "22", 120_000_000, "IV", "travaux routes", -55),
    ("Construction ecole primaire 6 classes", "APC Setif", "19", 58_000_000, "III", "batiment public", -52),
    ("Etude hydraulique barrage Koudiat", "Agence Nationale des Barrages", "16", 18_000_000, "III", "etudes hydraulique", -50),
    ("Fourniture mobilier scolaire 3 etablissements", "Direction Education Oran", "31", 22_000_000, None, "fournitures", -48),
    ("Entretien espaces verts communaux", "APC Ghardaia", "47", 8_500_000, None, "services", -45),
    ("Construction logement LPP 40 unites", "OPGI Blida", "09", 185_000_000, "IV", "batiment logement", -42),
    ("VRD lotissement 120 lots", "EPWG Blida", "09", 95_000_000, "III", "travaux VRD", -38),
    ("Installation electrique hopital Bourouba", "Direction Sante Alger", "16", 48_000_000, "III", "electricite batiment", -34),
    ("Pose reseau AEP zone industrielle", "ADE Annaba", "23", 72_000_000, "III", "travaux hydraulique VRD", -30),
    ("Fourniture materiel medical pediatrie", "CHU Oran", "31", 14_500_000, None, "fournitures medical", -26),
    ("Realisation piste agricole 8 km", "Direction Agriculture Ghardaia", "47", 32_000_000, "III", "travaux routes", -22),
    ("Fourniture semences bles 120 tonnes", "OAIC Annaba", "23", 18_000_000, None, "fournitures agricoles", -18),
    # Perdus (6 suivants)
    ("Restauration facades centre historique", "Direction Culture Setif", "19", 42_000_000, "IV", "batiment restauration", -54),
    ("Equipement informatique wilayas 15 postes", "Direction Executive Oran", "31", 9_800_000, None, "fournitures informatique", -47),
    ("Travaux assainissement quartier Dekkara", "APC Blida", "09", 56_000_000, "III", "travaux VRD", -40),
    ("Etude avant-projet station epuration", "ONA Alger", "16", 24_000_000, "III", "etudes hydraulique", -32),
    ("Fourniture uniformes scolaires 2500 eleves", "Direction Education Ghardaia", "47", 11_200_000, None, "fournitures textile", -25),
    ("Refection toiture etablissement scolaire", "DLEP Annaba", "23", 7_800_000, "III", "batiment public", -15),
    # En cours (2 derniers)
    ("Construction centre de sante rural", "Direction Sante SBA", "22", 78_000_000, "IV", "batiment public sante", -8),
    ("Fourniture et pose climatisation salles", "Universite Oran", "31", 26_500_000, "III", "climatisation", -4),
]


# Messages types client <-> assistant (realistes)
MESSAGES_MISSION = [
    ("client", "Bonjour, je vous transmets le cahier des charges en piece jointe. Date limite lundi 17h."),
    ("assistant", "Bien recu. Je commence l'analyse et je reviens vers vous d'ici demain matin avec les points d'attention."),
    ("assistant", "Apres analyse : quelques points a clarifier. La qualification requise est IV mais votre certificat indique III. Pouvez-vous confirmer la date de renouvellement ?"),
    ("client", "Le renouvellement est en cours, cabinet d'etudes Hadj en charge. Attestation provisoire dispo si besoin."),
    ("assistant", "Parfait, je l'inclus au dossier. Le chiffrage est pret : 78.5 MDA HT. Je vous envoie le detail pour validation."),
    ("client", "Validation OK de mon cote. Allez-y pour le depot."),
    ("assistant", "Dossier complet livre. Depot physique effectue ce matin 09h42, accuse de reception joint. Tout le meilleur pour l'attribution."),
]


# =============================================================================
# Helpers
# =============================================================================

def _user_exists(db, email: str) -> bool:
    return db.query(User).filter(User.email == email).first() is not None


def _ensure_user(db, *, organisation_id: int, email: str, username: str,
                 password: str, role: str) -> User:
    existing = db.query(User).filter(User.email == email).one_or_none()
    if existing:
        return existing
    u = User(
        organisation_id=organisation_id, email=email, username=username,
        password_hash=hash_password(password), role=role, actif=True,
        last_login=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 5)),
    )
    db.add(u); db.flush()
    return u


def _utc(d: date, hour: int = 10, minute: int = 0) -> datetime:
    return datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc).replace(
        hour=hour, minute=minute
    )


# =============================================================================
# Seed chunks
# =============================================================================

def seed_admin(db) -> User:
    if _user_exists(db, "admin@soumission.dz"):
        log("Admin deja present.")
        return db.query(User).filter(User.email == "admin@soumission.dz").first()

    org = Organisation(
        nom="SOUMISSION.DZ — Admin", type=OrgType.ENTREPRISE.value,
        plan=PlanCode.BUSINESS.value, statut=OrgStatut.ACTIF.value,
    )
    db.add(org); db.flush()
    admin = _ensure_user(db, organisation_id=org.id,
                         email="admin@soumission.dz", username="admin",
                         password="Admin12345", role=UserRole.ADMIN_PLATEFORME.value)
    db.commit()
    log("Admin cree : admin@soumission.dz / Admin12345")
    return admin


def seed_assistants(db) -> list[AssistantAgree]:
    """Cree 2 assistants agrees realistes avec historique."""
    org_tech = (db.query(Organisation)
                .filter(Organisation.nom == "SOUMISSION.DZ — Assistants")
                .one_or_none())
    if org_tech is None:
        org_tech = Organisation(
            nom="SOUMISSION.DZ — Assistants", type=OrgType.ENTREPRISE.value,
            plan=PlanCode.BUSINESS.value, statut=OrgStatut.ACTIF.value,
        )
        db.add(org_tech); db.flush()

    assistants_data = [
        ("yacine.assistant@soumission.dz", "yacine", "Yacine Merabet",
         ["BTPH", "VRD", "hydraulique"], "DZ59 0000 1111 2222 3333", 92, 18),
        ("samira.assistant@soumission.dz", "samira", "Samira Bouguerra",
         ["fournitures", "services", "etudes"], "DZ59 0000 4444 5555 6666", 88, 14),
    ]
    assts = []
    for email, username, _nom, specialites, iban, note, nb_missions in assistants_data:
        existing = db.query(AssistantAgree).join(User).filter(User.email == email).first()
        if existing:
            assts.append(existing)
            continue
        u = _ensure_user(db, organisation_id=org_tech.id,
                         email=email, username=username, password="Demo12345",
                         role=UserRole.ASSISTANT_AGREE.value)
        a = AssistantAgree(
            user_id=u.id, specialites=specialites, iban=iban,
            charte_signee_at=datetime.now(timezone.utc) - timedelta(days=120),
            actif=True, note_moyenne=note, nb_missions_terminees=nb_missions,
        )
        db.add(a); db.flush()
        assts.append(a)
    db.commit()
    log(f"{len(assts)} assistants agrees (Yacine + Samira).")
    return assts


def seed_plans(db) -> None:
    from app.routers.billing import PLANS_SEED
    if db.query(Plan).first():
        return
    for code, nom, m, a in PLANS_SEED:
        db.add(Plan(code=code, nom=nom, prix_mensuel_da=m, prix_annuel_da=a, actif=True))
    db.commit()


def seed_prestations(db) -> None:
    from app.models.phase4 import PRESTATIONS_SEED
    if db.query(PrestationCatalogue).first():
        return
    for code, nom, desc, prix, delai in PRESTATIONS_SEED:
        db.add(PrestationCatalogue(
            code=code, nom=nom, description=desc,
            prix_ht_da=prix, delai_max_jours=delai, actif=True,
        ))
    db.commit()


def seed_entreprise_cas1(db, data: dict) -> Entreprise:
    existing = db.query(Entreprise).filter(Entreprise.nom == data["nom"]).first()
    if existing:
        return existing
    org = Organisation(
        nom=data["nom"], type=OrgType.ENTREPRISE.value,
        plan=data["plan"], statut=OrgStatut.ACTIF.value,
    )
    db.add(org); db.flush()
    ent = Entreprise(
        organisation_id=org.id,
        nom=data["nom"], forme_juridique=data["forme_juridique"],
        nif=data["nif"], nis=data.get("nis"), rc=data.get("rc"),
        gerant=data.get("gerant"),
        wilaya_code=data["wilaya_code"], wilaya_nom=data["wilaya_nom"],
        adresse=data.get("adresse"), telephone=data.get("telephone"),
        email=data["email"], secteur=data["secteur"],
        activite=data.get("activite"), effectif=data.get("effectif"),
        ca_moyen_da=data.get("ca_moyen_da"),
        qualification_cat=data.get("qualification_cat"),
        qualification_expiration=data.get("qualification_expiration"),
    )
    db.add(ent); db.flush()
    _ensure_user(db, organisation_id=org.id,
                 email=data["email"], username=data["patron"],
                 password="Demo12345", role=UserRole.PATRON.value)
    db.commit()
    return ent


def seed_cabinet_mourad(db) -> tuple[Cabinet, list[Entreprise]]:
    """Cree le cabinet Mourad + 3 entreprises dans son portefeuille."""
    existing_cab = db.query(Cabinet).filter(Cabinet.nom == "Cabinet Mourad Conseils").first()
    if existing_cab:
        return existing_cab, existing_cab.entreprises

    org = Organisation(
        nom="Cabinet Mourad Conseils", type=OrgType.CABINET.value,
        plan=PlanCode.EXPERT.value, statut=OrgStatut.ACTIF.value,
    )
    db.add(org); db.flush()

    cab = Cabinet(
        organisation_id=org.id, nom="Cabinet Mourad Conseils",
        consultant_principal="Mourad Hadjadj",
        email="mourad@cabinet-mourad.dz", telephone="+213 23 90 12 34",
        wilaya_code="16",
    )
    db.add(cab); db.flush()

    _ensure_user(db, organisation_id=org.id,
                 email="mourad@cabinet-mourad.dz", username="mourad",
                 password="Demo12345", role=UserRole.CONSULTANT.value)

    # 3 entreprises dans le portefeuille
    entreprises = []
    for data in ENTREPRISES_PORTEFEUILLE_MOURAD:
        existing = db.query(Entreprise).filter(Entreprise.nom == data["nom"]).first()
        if existing:
            entreprises.append(existing)
            continue
        ent = Entreprise(
            cabinet_id=cab.id,  # attache au cabinet, pas d'organisation propre
            nom=data["nom"], forme_juridique=data["forme_juridique"],
            nif=data["nif"], nis=data.get("nis"), rc=data.get("rc"),
            gerant=data.get("gerant"),
            wilaya_code=data["wilaya_code"], wilaya_nom=data["wilaya_nom"],
            adresse=data.get("adresse"), telephone=data.get("telephone"),
            email=data["email"], secteur=data["secteur"],
            activite=data.get("activite"), effectif=data.get("effectif"),
            ca_moyen_da=data.get("ca_moyen_da"),
            qualification_cat=data.get("qualification_cat"),
            qualification_expiration=data.get("qualification_expiration"),
        )
        db.add(ent); db.flush()
        entreprises.append(ent)

    db.commit()
    log(f"Cabinet Mourad cree + {len(entreprises)} entreprises en portefeuille.")
    return cab, entreprises


def seed_coffre(db, ent: Entreprise) -> None:
    """Remplit le coffre de l'entreprise avec docs + PDFs factices."""
    if db.query(Document).filter(Document.entreprise_id == ent.id).first():
        return

    from app.config import get_settings
    storage = get_settings().storage_path
    dest = storage / str(ent.id) / "documents"
    dest.mkdir(parents=True, exist_ok=True)

    for code, exp_days in DOCS_PAR_ENTREPRISE:
        # CACOBATPH et QUALIFICATION_BTPH sont pour BTPH uniquement
        if code in {"CACOBATPH", "QUALIFICATION_BTPH"} and ent.secteur != "BTPH":
            continue
        expir = (TODAY + timedelta(days=exp_days)) if exp_days else None
        content = f"%PDF-1.4\n% Document {code} de {ent.nom}\n".encode()
        d = Document(
            entreprise_id=ent.id, type_code=code,
            filename=f"{code}_{ent.nom.replace(' ','_')}.pdf",
            stored_path="", size_bytes=len(content),
            date_emission=TODAY - timedelta(days=random.randint(30, 365)),
            date_expiration=expir,
        )
        db.add(d); db.flush()
        path = dest / f"{d.id}_{d.filename}"
        path.write_bytes(content)
        d.stored_path = str(path)
    db.commit()


def seed_references(db, ent: Entreprise) -> None:
    """3 a 6 references historiques par entreprise."""
    if db.query(Reference).filter(Reference.entreprise_id == ent.id).first():
        return

    n = random.randint(3, 6)
    types_dispo = {
        "BTPH": [("routes", "Direction TP"), ("batiment public", "OPGI"),
                 ("VRD", "APC"), ("batiment logement", "AADL")],
        "Etudes": [("etudes hydraulique", "ANBT"), ("etudes VRD", "DUAC")],
        "Fournitures": [("fournitures", "CHU"), ("fournitures medicales", "Direction Sante")],
        "Services": [("entretien", "APC"), ("services administratifs", "Wilaya")],
        "Electricite": [("electricite batiment", "Direction Sante"), ("electricite", "Universite")],
    }
    types = types_dispo.get(ent.secteur, [("divers", "Administration")])

    for i in range(n):
        type_trav, mo_type = random.choice(types)
        annee = random.randint(2020, 2024)
        montant = random.randint(15, 200) * 1_000_000
        objets = {
            "routes": "Realisation de voirie",
            "batiment public": "Construction de batiment public",
            "VRD": "Travaux VRD",
            "batiment logement": "Construction de logements",
            "etudes hydraulique": "Etude hydraulique",
            "etudes VRD": "Etude VRD",
            "fournitures": "Fourniture de materiel",
            "fournitures medicales": "Fourniture materiel medical",
            "entretien": "Entretien d'espaces",
            "services administratifs": "Prestation de services",
            "electricite batiment": "Installation electrique",
            "electricite": "Travaux electriques",
            "divers": "Prestation diverse",
        }
        db.add(Reference(
            entreprise_id=ent.id,
            objet=f"{objets.get(type_trav, 'Prestation')} - projet {i+1}",
            maitre_ouvrage=f"{mo_type} {ent.wilaya_nom}",
            montant_da=montant, annee=annee, type_travaux=type_trav,
        ))
    db.commit()


def seed_abonnement_et_factures(db, org: Organisation) -> None:
    """Abonnement actif depuis 2 mois + 2 factures mensuelles, la plus ancienne payee."""
    if db.query(Abonnement).filter(Abonnement.organisation_id == org.id).first():
        return

    plan = db.query(Plan).filter(Plan.code == org.plan).one_or_none()
    if plan is None or plan.prix_mensuel_da == 0:
        return

    debut = TODAY - timedelta(days=60)
    abo = Abonnement(
        organisation_id=org.id, plan_id=plan.id,
        periodicite="mensuel", debut=debut,
        fin=debut + timedelta(days=60),
        statut="actif",
    )
    db.add(abo); db.flush()

    # Facture mois M-2 (payee) + mois M-1 (payee) + mois en cours (emise)
    for i in range(2):
        emission = TODAY - timedelta(days=60 - i * 30)
        numero = _next_facture_numero(db, emission.year)
        ht = plan.prix_mensuel_da
        ttc = int(round(ht * 1.19))
        f = Facture(
            organisation_id=org.id, numero=numero, annee=emission.year,
            abonnement_id=abo.id,
            date_emission=emission, date_echeance=emission + timedelta(days=15),
            libelle=f"Abonnement {plan.nom} - mois {(emission.month):02d}/{emission.year}",
            prix_ht_da=ht, tva_pct=19, prix_ttc_da=ttc,
            mode_paiement="edahabia", statut="payee",
            paiement_recu_at=_utc(emission + timedelta(days=random.randint(1, 12))),
        )
        db.add(f); db.flush()

    # Facture du mois en cours (emise, pas encore payee)
    emission = TODAY - timedelta(days=5)
    f = Facture(
        organisation_id=org.id,
        numero=_next_facture_numero(db, emission.year), annee=emission.year,
        abonnement_id=abo.id,
        date_emission=emission, date_echeance=emission + timedelta(days=15),
        libelle=f"Abonnement {plan.nom} - mois {(emission.month):02d}/{emission.year}",
        prix_ht_da=plan.prix_mensuel_da, tva_pct=19,
        prix_ttc_da=int(round(plan.prix_mensuel_da * 1.19)),
        statut="emise",
    )
    db.add(f)
    db.commit()


_facture_counter = {}


def _next_facture_numero(db, annee: int) -> str:
    if annee not in _facture_counter:
        last = (db.query(Facture).filter(Facture.annee == annee)
                .order_by(Facture.id.desc()).first())
        _facture_counter[annee] = int(last.numero.split("-")[-1]) if last else 0
    _facture_counter[annee] += 1
    return f"SDZ-{annee}-{_facture_counter[annee]:05d}"


def seed_ao_et_soumissions(db, entreprises: list[Entreprise]) -> None:
    """20 AO sur 2 mois repartis entre les entreprises, 60% gagnes."""
    if db.query(AppelOffres).count() >= 20:
        log("AO deja seedes.")
        return

    random.seed(20260413)  # reproductibilite pour les affectations
    if not entreprises:
        return

    # Assignation des 20 AO aux entreprises en tenant compte du secteur
    secteur_to_ents = {}
    for e in entreprises:
        secteur_to_ents.setdefault(e.secteur, []).append(e)

    ao_type_to_secteur = {
        "travaux routes": "BTPH",
        "batiment public": "BTPH",
        "batiment logement": "BTPH",
        "batiment public sante": "BTPH",
        "batiment restauration": "BTPH",
        "travaux VRD": "BTPH",
        "travaux hydraulique VRD": "BTPH",
        "etudes hydraulique": "Etudes",
        "fournitures": "Fournitures",
        "fournitures medical": "Fournitures",
        "fournitures informatique": "Fournitures",
        "fournitures textile": "Fournitures",
        "fournitures agricoles": "Fournitures",
        "services": "Services",
        "electricite batiment": "Electricite",
        "climatisation": "Electricite",
    }

    # Distribution equilibree : on garantit a chaque entreprise 2 AO minimum.
    # On assigne chaque AO au candidat (compatible secteur) qui a le moins d'AO.
    assignment = {e.id: 0 for e in entreprises}

    def _pick_candidate(activites: str) -> Entreprise:
        secteur_cible = ao_type_to_secteur.get(activites, "BTPH")
        candidats = secteur_to_ents.get(secteur_cible)
        if not candidats:
            candidats = (secteur_to_ents.get("BTPH") or
                         [e for lst in secteur_to_ents.values() for e in lst])
        # Choisir le candidat avec le moins d'AO deja assignes (tirage aleatoire en cas d'egalite)
        candidats_sorted = sorted(candidats, key=lambda e: (assignment[e.id], random.random()))
        return candidats_sorted[0]

    ao_created = 0
    for i, (objet, mo, wil, budget, qual_cat, activites, jours) in enumerate(AO_TEMPLATE):
        ent = _pick_candidate(activites)
        assignment[ent.id] += 1
        date_limite = TODAY + timedelta(days=jours + random.randint(14, 30))
        date_pub = TODAY + timedelta(days=jours)

        ao = AppelOffres(
            entreprise_id=ent.id,
            reference=f"AO-{date_pub.year}/{100 + i:03d}",
            objet=objet, maitre_ouvrage=mo, wilaya_code=wil,
            date_limite=date_limite, budget_estime_da=budget,
            qualification_requise_cat=qual_cat,
            qualification_requise_activites=activites,
        )
        db.add(ao); db.flush()
        ao_created += 1

        # Determine l'issue selon l'index dans AO_TEMPLATE
        if i < 12:
            issue = "gagne"
        elif i < 18:
            issue = "perdu"
        else:
            issue = "en_cours"

        # Dossier associe
        if issue == "en_cours":
            # Dossier en cours : audit, chiffrage, memoire ou verification
            etapes_possibles = ["audit", "chiffrage", "memoire", "verification"]
            etape = random.choice(etapes_possibles)
            d = Dossier(
                entreprise_id=ent.id, ao_id=ao.id,
                nom=f"Dossier {ao.reference}",
                statut="en_cours", etape_actuelle=etape,
                score_audit=random.randint(72, 92),
                date_cible=date_limite - timedelta(days=2),
            )
            db.add(d); db.flush()

            # Caution soumission 1% (active)
            db.add(Caution(
                entreprise_id=ent.id, dossier_id=d.id, type_code="caution_soumission",
                montant_da=int(budget * 0.01),
                banque=random.choice(["BNA", "CPA", "BDL", "BEA"]),
                date_emission=TODAY - timedelta(days=random.randint(1, 10)),
                date_recuperation_estimee=date_limite + timedelta(days=90),
                statut="active",
                reference_bancaire=f"CS-{random.randint(100000, 999999)}",
            ))

        else:
            # Dossier termine + soumission deposee
            depot_date = date_pub + timedelta(days=random.randint(14, 28))
            d = Dossier(
                entreprise_id=ent.id, ao_id=ao.id,
                nom=f"Dossier {ao.reference}",
                statut="termine", etape_actuelle="depot",
                score_audit=random.randint(78, 95) if issue == "gagne" else random.randint(60, 82),
                date_cible=depot_date,
            )
            db.add(d); db.flush()

            if issue == "gagne":
                rang = 1
                montant_s = int(budget * random.uniform(0.85, 0.98))
                montant_att = montant_s  # l'entreprise est elle-meme attributaire
                ecart = 0
                raison = random.choice([
                    "Offre technique bien notee + prix competitif.",
                    "Meilleure capacite financiere + references pertinentes.",
                    "Delai d'execution plus court que les concurrents.",
                    "Qualification adequate + experience demontree.",
                ])
            else:  # perdu
                rang = random.randint(2, 6)
                montant_s = int(budget * random.uniform(0.90, 1.05))
                # Attributaire a un prix plus bas
                montant_att = int(montant_s * random.uniform(0.82, 0.95))
                ecart = int(round((montant_s - montant_att) / max(montant_att, 1) * 100))
                raison = random.choice([
                    "Prix plus eleve que l'attributaire.",
                    "Note technique inferieure au concurrent.",
                    "Capacite financiere jugee insuffisante.",
                    "References dans le domaine moins nombreuses.",
                ])

            db.add(Soumission(
                entreprise_id=ent.id, ao_id=ao.id, dossier_id=d.id,
                date_depot=depot_date, rang=rang,
                montant_soumissionne_da=montant_s,
                montant_attributaire_da=montant_att,
                ecart_pct=ecart, statut=issue, raison_libre=raison,
            ))

            # Caution soumission (recuperee si perdu, toujours active si gagne pour le depot)
            caution_statut = "recuperee" if issue == "perdu" else "active"
            db.add(Caution(
                entreprise_id=ent.id, dossier_id=d.id, type_code="caution_soumission",
                montant_da=int(budget * 0.01),
                banque=random.choice(["BNA", "CPA", "BDL", "BEA"]),
                date_emission=depot_date - timedelta(days=5),
                date_recuperation_estimee=depot_date + timedelta(days=90),
                statut=caution_statut,
                reference_bancaire=f"CS-{random.randint(100000, 999999)}",
            ))

            # Gagnes : caution de bonne execution 5% (active, en cours d'execution)
            if issue == "gagne":
                db.add(Caution(
                    entreprise_id=ent.id, dossier_id=d.id, type_code="garantie_bonne_execution",
                    montant_da=int(montant_att * 0.05),
                    banque=random.choice(["BNA", "CPA", "BDL", "BEA"]),
                    date_emission=depot_date + timedelta(days=35),
                    date_recuperation_estimee=depot_date + timedelta(days=365),
                    statut="active",
                    reference_bancaire=f"BE-{random.randint(100000, 999999)}",
                ))

    db.commit()
    log(f"{ao_created} AO seedes (12 gagnes / 6 perdus / 2 en cours).")


def seed_missions_cas3(db, assistants: list[AssistantAgree]) -> None:
    """4 missions Cas 3 dans differents etats."""
    if db.query(Mission).count() >= 4:
        return

    # On choisit 4 entreprises clientes au hasard
    clients = db.query(Entreprise).join(
        Organisation, Entreprise.organisation_id == Organisation.id
    ).filter(Organisation.type == OrgType.ENTREPRISE.value).limit(4).all()
    if not clients:
        return

    prestations = {p.code: p for p in db.query(PrestationCatalogue).all()}
    if not prestations or not assistants:
        return

    scenarios = [
        # (client_idx, prestation, statut, jours_depuis_creation)
        (0, "DOSSIER_CLE_EN_MAIN", "validee", 35),   # Mission cloturee, note 5
        (1, "URGENCE_72H", "en_cours", 2),           # En cours de traitement
        (2, "REDACTION_MEMOIRE", "livree", 5),       # Livree, en attente validation
        (3, "CHIFFRAGE_DQE", "brouillon", 1),        # Juste demandee
    ]

    for idx, presta_code, statut, jours in scenarios:
        if idx >= len(clients):
            continue
        client = clients[idx]
        presta = prestations.get(presta_code)
        if presta is None:
            continue

        created_at = datetime.now(timezone.utc) - timedelta(days=jours)
        asst = assistants[idx % len(assistants)]

        m = Mission(
            entreprise_id=client.id, prestation_id=presta.id,
            brief=(f"Demande d'assistance pour prestation {presta.nom}. "
                   f"AO : construction/fourniture en cours. Contraintes de delai serrees."),
            statut=statut,
            prix_ht_da=presta.prix_ht_da, tva=19,
            prix_ttc_da=int(round(presta.prix_ht_da * 1.19)),
        )
        # Force created_at
        m.created_at = created_at
        m.updated_at = created_at

        # Enchainer les etapes selon le statut cible
        if statut in ("en_cours", "livree", "validee", "contestee"):
            m.assistant_id = asst.id
            m.affectee_at = created_at + timedelta(hours=2)
            m.demarree_at = created_at + timedelta(hours=3)
        if statut in ("livree", "validee", "contestee"):
            m.livree_at = created_at + timedelta(days=2)
            m.livrables = ["dossier_complet.zip", "memoire_technique.docx", "dqe.xlsx"]
        if statut == "validee":
            m.validee_at = created_at + timedelta(days=3)
            m.note_client = 5
            m.commentaire_client = "Prestation impeccable, delai respecte."
            m.paiement_assistant_statut = "paye"

        db.add(m); db.flush()

        # Mandat
        if statut != "brouillon":
            mandat = Mandat(
                entreprise_id=client.id, mission_id=m.id, assistant_id=asst.id,
                signe_at=created_at + timedelta(hours=1),
                signe_ip="197.0.0.1",
                signe_user_agent="Mozilla/5.0 (Windows)",
                valide_du=created_at.date(),
                valide_jusqu_au=created_at.date() + timedelta(days=presta.delai_max_jours),
                perimetre_actions=["lecture_dossier", "modification_dossier",
                                   "upload_documents", "depot"],
                statut="signe" if statut != "validee" else "execute",
            )
            db.add(mandat); db.flush()

            # Messagerie
            num_msgs = min(len(MESSAGES_MISSION),
                           {"en_cours": 3, "livree": 6, "validee": 7, "contestee": 6}[statut])
            for j, (role, txt) in enumerate(MESSAGES_MISSION[:num_msgs]):
                if role == "client":
                    auteur_id = (db.query(User)
                                 .filter(User.organisation_id == client.organisation_id)
                                 .first().id)
                else:
                    auteur_id = asst.user_id
                msg_time = created_at + timedelta(hours=1 + j * 6)
                msg = MissionMessage(
                    mission_id=m.id, auteur_user_id=auteur_id,
                    role_auteur=role, message=txt,
                )
                msg.created_at = msg_time
                msg.updated_at = msg_time
                db.add(msg)

            # Journal d'actions
            if statut in ("livree", "validee", "contestee"):
                db.add(AoMandatAction(
                    mandat_id=mandat.id, user_id_assistant=asst.user_id,
                    action_type="livraison_mission",
                    action_payload={"livrables": m.livrables, "mission_id": m.id},
                ))

    db.commit()
    log("4 missions Cas 3 seedees (1 validee, 1 en cours, 1 livree, 1 brouillon).")


def seed_hotline_tickets(db) -> None:
    """8 tickets hotline varies."""
    if db.query(TicketHotline).count() >= 5:
        return

    orgs = db.query(Organisation).filter(
        Organisation.type == OrgType.ENTREPRISE.value,
        Organisation.nom.notin_(["SOUMISSION.DZ — Admin", "SOUMISSION.DZ — Assistants"]),
    ).all()
    if not orgs:
        return

    tickets_data = [
        ("technique", "Probleme upload PDF volumineux",
         "Le PDF de 15 Mo refuse de s'uploader, j'ai essaye plusieurs fois.", "resolu",
         "Merci, nous avons augmente la limite a 25 Mo. Reessayez."),
        ("conseil", "Qualification BTPH cat IV pour AO route",
         "Ai-je besoin de la qualification IV specifiquement pour cet AO ou III suffit ?", "resolu",
         "La qualification III peut suffire pour les tranches < 100 MDA. Verifiez l'article 8 du CPT."),
        ("expertise", "Redaction memoire technique pour AO hopital",
         "Avez-vous un exemple type de memoire pour un AO de construction d'hopital 200 lits ?", "resolu",
         "Nous vous proposons une prestation d'assistance dediee. Un devis vous sera envoye."),
        ("technique", "Erreur lors de l'import PDF AO",
         "L'extraction ne recupere pas la date limite sur les AO de la wilaya d'Alger.", "ouvert", None),
        ("conseil", "Retenue de garantie de 5%, est-ce obligatoire ?",
         "Le CPT mentionne 10%, est-ce negociable avec le MO ?", "resolu",
         "La retenue de garantie est plafonnee a 10% par l'art 98 du decret 247-15. Negociable jusqu'a 5%."),
        ("technique", "Impossibilite de generer le formulaire de probite",
         "Le bouton renvoie une erreur 500.", "resolu",
         "Bug corrige dans la version 5.0.1. Relancez la generation."),
        ("conseil", "Delai de publication avant depot",
         "Quel est le delai minimum legal entre publication et date limite ?", "ouvert", None),
        ("expertise", "AO restreint, comment candidater ?",
         "Le MO nous a invites a un AO restreint, quelle procedure specifique ?", "resolu",
         "Verifiez la presence dans la liste restreinte. Dossier administratif simplifie acceptable."),
    ]

    admin_user = db.query(User).filter(User.role == UserRole.ADMIN_PLATEFORME.value).first()

    for i, (niveau, sujet, desc, statut, reponse) in enumerate(tickets_data):
        org = orgs[i % len(orgs)]
        emetteur = db.query(User).filter(User.organisation_id == org.id).first()
        created = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 55))
        t = TicketHotline(
            organisation_id=org.id,
            user_id_emetteur=emetteur.id if emetteur else None,
            niveau=niveau, sujet=sujet, description=desc, statut=statut,
        )
        t.created_at = created
        t.updated_at = created
        if statut == "resolu":
            t.user_id_operateur = admin_user.id if admin_user else None
            t.reponse = reponse
            t.resolu_at = created + timedelta(hours=random.randint(2, 48))
        db.add(t)
    db.commit()
    log(f"{len(tickets_data)} tickets hotline seedes.")


def seed_parrainage(db) -> None:
    """Codes de parrainage + quelques commissions mensuelles."""
    if db.query(CodeParrainage).count() >= 3:
        return

    users = db.query(User).filter(
        User.role.in_([UserRole.PATRON.value, UserRole.CONSULTANT.value])
    ).limit(6).all()

    for u in users:
        if db.query(CodeParrainage).filter(CodeParrainage.user_id == u.id).first():
            continue
        db.add(CodeParrainage(
            user_id=u.id,
            code=f"SDZ-{secrets.token_hex(4).upper()}",
            actif=True,
        ))
    db.flush()

    # 3 commissions de parrainage pour le consultant Mourad (il est le meilleur parrain)
    consultant = db.query(User).filter(
        User.role == UserRole.CONSULTANT.value
    ).first()
    if consultant:
        orgs_pro = (db.query(Organisation)
                    .filter(Organisation.type == OrgType.ENTREPRISE.value,
                            Organisation.plan == PlanCode.PRO.value)
                    .limit(3).all())
        for i, org_filleule in enumerate(orgs_pro):
            mois = TODAY.replace(day=1) - timedelta(days=30 * i)
            db.add(Commission(
                parrain_user_id=consultant.id,
                organisation_filleule_id=org_filleule.id,
                mois=mois.strftime("%Y-%m"),
                montant_commission_da=int(10000 * 0.20),  # 20% de PRO 10k = 2000 DA
                statut="payee" if i > 0 else "en_attente",
            ))
    db.commit()
    log("Codes parrainage + 3 commissions Mourad seedes.")


# =============================================================================
# Main
# =============================================================================

def main() -> int:
    db = SessionLocal()
    try:
        log("=" * 70)
        log("INSERTION DES SEEDS DE DEMONSTRATION (plateforme 2 mois d'activite)")
        log("=" * 70)

        # Catalogues de reference
        seed_plans(db)
        seed_prestations(db)
        n_articles = seed_prix_articles(db)
        log(f"Catalogues : plans OK, prestations OK, {n_articles} articles BTPH.")

        # Utilisateurs
        seed_admin(db)
        assistants = seed_assistants(db)

        # Entreprises Cas 1
        ents_cas1 = []
        for data in ENTREPRISES_CAS1:
            e = seed_entreprise_cas1(db, data)
            ents_cas1.append(e)
        log(f"{len(ents_cas1)} entreprises Cas 1 creees.")

        # Cabinet Cas 2 + 3 entreprises en portefeuille
        _cabinet, ents_mourad = seed_cabinet_mourad(db)

        # Toutes les entreprises reunies (8 au total)
        all_entreprises = ents_cas1 + ents_mourad
        log(f"Total : {len(all_entreprises)} entreprises (5 Cas 1 + 3 portefeuille Mourad).")

        # Coffre + references pour chaque entreprise
        for e in all_entreprises:
            seed_coffre(db, e)
            seed_references(db, e)
        log(f"Coffre-fort + references peuples pour {len(all_entreprises)} entreprises.")

        # Abonnements + factures pour les orgs Cas 1 + cabinet
        orgs_cas1 = [e.organisation for e in ents_cas1 if e.organisation]
        cab_org = db.query(Organisation).filter(
            Organisation.nom == "Cabinet Mourad Conseils"
        ).first()
        if cab_org:
            orgs_cas1.append(cab_org)
        for org in orgs_cas1:
            seed_abonnement_et_factures(db, org)
        log(f"Abonnements + factures SOUMISSION.DZ seedes ({len(orgs_cas1)} organisations).")

        # AO + soumissions (cœur de la demo)
        seed_ao_et_soumissions(db, all_entreprises)

        # Missions Cas 3
        seed_missions_cas3(db, assistants)

        # Hotline + parrainage
        seed_hotline_tickets(db)
        seed_parrainage(db)

        log("=" * 70)
        log("Comptes de demonstration :")
        log("  ADMIN   : admin@soumission.dz            / Admin12345")
        log("  CAS 1   : brahim@alpha-btph.dz           / Demo12345  (Sidi Bel Abbes)")
        log("          : kamel@batipro-setif.dz         / Demo12345  (Setif)")
        log("          : amine@hydra-etudes.dz          / Demo12345  (Alger etudes)")
        log("          : nadia@omega-fournitures.dz     / Demo12345  (Oran)")
        log("          : omar@sud-travaux.dz            / Demo12345  (Ghardaia)")
        log("  CAS 2   : mourad@cabinet-mourad.dz       / Demo12345  (3 entreprises)")
        log("  CAS 3   : yacine.assistant@soumission.dz / Demo12345  (BTPH+VRD)")
        log("          : samira.assistant@soumission.dz / Demo12345  (fournitures)")
        log("=" * 70)

        # Synthese
        stats = {
            "Entreprises totales": db.query(Entreprise).count(),
            "Users": db.query(User).count(),
            "Appels d'offres": db.query(AppelOffres).count(),
            "Soumissions": db.query(Soumission).count(),
            "  dont gagnees": db.query(Soumission).filter(Soumission.statut == "gagne").count(),
            "  dont perdues": db.query(Soumission).filter(Soumission.statut == "perdu").count(),
            "Dossiers": db.query(Dossier).count(),
            "Documents coffre": db.query(Document).count(),
            "References": db.query(Reference).count(),
            "Cautions": db.query(Caution).count(),
            "Abonnements": db.query(Abonnement).count(),
            "Factures": db.query(Facture).count(),
            "Missions Cas 3": db.query(Mission).count(),
            "Tickets hotline": db.query(TicketHotline).count(),
            "Codes parrainage": db.query(CodeParrainage).count(),
        }
        log("Synthese de la base peuplee :")
        for k, v in stats.items():
            log(f"  {k:28s} : {v}")

        total_gagne = db.query(Soumission).filter(Soumission.statut == "gagne").count()
        total_final = db.query(Soumission).filter(
            Soumission.statut.in_(["gagne", "perdu"])
        ).count()
        if total_final:
            log(f"  Taux de gain                 : {100 * total_gagne / total_final:.0f}%")

        # CA cumule gagne
        ca = (db.query(Soumission)
              .filter(Soumission.statut == "gagne")
              .with_entities(Soumission.montant_attributaire_da).all())
        ca_total = sum(s[0] or 0 for s in ca)
        log(f"  CA cumule marches gagnes     : {ca_total:,} DA".replace(",", " "))
        log("=" * 70)

    except Exception as e:
        log(f"ERREUR : {e}")
        import traceback; traceback.print_exc()
        return 1
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
