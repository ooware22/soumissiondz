# -*- coding: utf-8 -*-
"""Seeds du catalogue de prix BTPH (35 articles) et des templates de marches (5)."""
from __future__ import annotations

# 35 articles BTPH — (code, libelle, unite, categorie, min, moy, max) en DA
PRIX_BTPH_SEED: list[tuple[str, str, str, str, int, int, int]] = [
    # Terrassement (5)
    ("TER001", "Decapage terre vegetale", "m3", "terrassement", 280, 350, 450),
    ("TER002", "Deblai en terrain meuble", "m3", "terrassement", 320, 400, 500),
    ("TER003", "Deblai en terrain rocheux", "m3", "terrassement", 900, 1200, 1600),
    ("TER004", "Remblai compacte", "m3", "terrassement", 380, 450, 550),
    ("TER005", "Evacuation deblais 10 km", "m3", "terrassement", 250, 320, 420),
    # Gros oeuvre (8)
    ("GRO001", "Beton de proprete dose 150", "m3", "gros_oeuvre", 7500, 9000, 11000),
    ("GRO002", "Beton arme dose 350 (fondations)", "m3", "gros_oeuvre", 24000, 28000, 33000),
    ("GRO003", "Beton arme dose 400 (superstructure)", "m3", "gros_oeuvre", 27000, 32000, 38000),
    ("GRO004", "Acier HA Fe400 en attente", "kg", "gros_oeuvre", 120, 140, 170),
    ("GRO005", "Coffrage courant", "m2", "gros_oeuvre", 850, 1100, 1400),
    ("GRO006", "Mur en parpaing 20 cm hourde mortier", "m2", "gros_oeuvre", 1400, 1700, 2100),
    ("GRO007", "Enduit tyrolien exterieur", "m2", "gros_oeuvre", 650, 800, 1000),
    ("GRO008", "Chape de lissage 4 cm", "m2", "gros_oeuvre", 550, 680, 850),
    # VRD (6)
    ("VRD001", "Pose canalisation PVC DN 200", "ml", "vrd", 1800, 2300, 2900),
    ("VRD002", "Regard de visite beton 0.80 x 0.80", "u", "vrd", 18000, 22000, 28000),
    ("VRD003", "Bordure T3", "ml", "vrd", 1400, 1700, 2100),
    ("VRD004", "Couche de base GNT 0/31.5", "m3", "vrd", 2800, 3400, 4100),
    ("VRD005", "Enrobe bitumineux EB 0/14", "tonne", "vrd", 14000, 17000, 20500),
    ("VRD006", "Trottoir beton epaisseur 10 cm", "m2", "vrd", 1600, 2000, 2500),
    # Electricite BT (4)
    ("ELE001", "Cable HO7RN-F 3G2.5", "ml", "electricite", 220, 280, 350),
    ("ELE002", "Cable U1000 R2V 4x16", "ml", "electricite", 650, 820, 1000),
    ("ELE003", "Disjoncteur differentiel 30 mA 40A", "u", "electricite", 4500, 5800, 7500),
    ("ELE004", "Luminaire LED plafonnier 24W", "u", "electricite", 2200, 2800, 3600),
    # Plomberie / sanitaire (4)
    ("PLO001", "Tube PPR PN20 DN 25", "ml", "plomberie", 280, 350, 440),
    ("PLO002", "WC complet standard", "u", "plomberie", 18000, 23000, 29000),
    ("PLO003", "Lavabo colonne porcelaine", "u", "plomberie", 14000, 18000, 22500),
    ("PLO004", "Chauffe-eau electrique 80 L", "u", "plomberie", 28000, 34000, 42000),
    # Menuiserie (3)
    ("MEN001", "Porte bois isoplane 90x210", "u", "menuiserie", 18000, 23000, 29000),
    ("MEN002", "Fenetre aluminium 1.50x1.20", "u", "menuiserie", 32000, 40000, 52000),
    ("MEN003", "Porte blindee entree", "u", "menuiserie", 75000, 95000, 125000),
    # Peinture (3)
    ("PEI001", "Peinture mate sur plafond", "m2", "peinture", 380, 480, 600),
    ("PEI002", "Peinture lessivable sur mur", "m2", "peinture", 450, 560, 700),
    ("PEI003", "Vernis sur menuiserie bois", "m2", "peinture", 800, 1000, 1300),
    # Etancheite (2)
    ("ETA001", "Etancheite multicouche sur toiture", "m2", "etancheite", 2200, 2800, 3500),
    ("ETA002", "Isolation thermique polystyrene 5 cm", "m2", "etancheite", 1100, 1400, 1800),
]


# 5 templates de marche avec DQE de base (postes + quantites normalisees pour un budget de reference)
# Les quantites sont ajustees proportionnellement au budget cible.
TEMPLATES_SEED: list[dict] = [
    {
        "code": "ROUTES",
        "nom": "Route rurale 1 km",
        "description": "Couche de base + enrobe + ouvrages d'assainissement",
        "budget_reference_da": 45_000_000,
        "postes": [
            {"code": "TER001", "quantite": 1200},
            {"code": "TER002", "quantite": 3500},
            {"code": "VRD001", "quantite": 500},
            {"code": "VRD004", "quantite": 2800},
            {"code": "VRD005", "quantite": 650},
            {"code": "VRD003", "quantite": 2000},
        ],
    },
    {
        "code": "BATIMENT_PUBLIC",
        "nom": "Batiment public (bureaux 500 m2)",
        "description": "Structure beton + cloisons + second oeuvre + electricite",
        "budget_reference_da": 65_000_000,
        "postes": [
            {"code": "GRO002", "quantite": 120},
            {"code": "GRO003", "quantite": 80},
            {"code": "GRO004", "quantite": 18000},
            {"code": "GRO005", "quantite": 600},
            {"code": "GRO006", "quantite": 750},
            {"code": "ELE001", "quantite": 2500},
            {"code": "ELE003", "quantite": 40},
            {"code": "MEN001", "quantite": 25},
            {"code": "MEN002", "quantite": 30},
            {"code": "PEI002", "quantite": 1500},
        ],
    },
    {
        "code": "VRD",
        "nom": "VRD lotissement 50 lots",
        "description": "Voirie + reseaux divers pour lotissement residentiel",
        "budget_reference_da": 55_000_000,
        "postes": [
            {"code": "TER001", "quantite": 3000},
            {"code": "TER002", "quantite": 8000},
            {"code": "VRD001", "quantite": 2500},
            {"code": "VRD002", "quantite": 50},
            {"code": "VRD003", "quantite": 5000},
            {"code": "VRD004", "quantite": 4500},
            {"code": "VRD005", "quantite": 850},
        ],
    },
    {
        "code": "LPP",
        "nom": "Logement LPP (bloc 60 logements)",
        "description": "Logement promotionnel public — structure + second oeuvre",
        "budget_reference_da": 180_000_000,
        "postes": [
            {"code": "GRO002", "quantite": 450},
            {"code": "GRO003", "quantite": 280},
            {"code": "GRO004", "quantite": 65000},
            {"code": "GRO005", "quantite": 2100},
            {"code": "GRO006", "quantite": 3200},
            {"code": "PLO002", "quantite": 60},
            {"code": "PLO003", "quantite": 60},
            {"code": "MEN001", "quantite": 180},
            {"code": "MEN002", "quantite": 240},
            {"code": "PEI001", "quantite": 3800},
            {"code": "ETA001", "quantite": 1200},
        ],
    },
    {
        "code": "HYDRAULIQUE",
        "nom": "Reseau AEP 2 km",
        "description": "Reseau d'adduction d'eau potable avec ouvrages associes",
        "budget_reference_da": 38_000_000,
        "postes": [
            {"code": "TER002", "quantite": 4200},
            {"code": "VRD001", "quantite": 2200},
            {"code": "VRD002", "quantite": 25},
            {"code": "TER004", "quantite": 3800},
        ],
    },
]


def seed_prix_articles(session) -> int:
    """Idempotent : insere les 35 articles s'ils n'existent pas deja."""
    from app.models import PrixArticle

    existing = {a.code for a in session.query(PrixArticle).all()}
    created = 0
    for code, libelle, unite, categorie, pmin, pmoy, pmax in PRIX_BTPH_SEED:
        if code in existing:
            continue
        session.add(PrixArticle(
            code=code, libelle=libelle, unite=unite, categorie=categorie,
            prix_min_da=pmin, prix_moy_da=pmoy, prix_max_da=pmax,
        ))
        created += 1
    session.commit()
    return created
