---
title: "SOUMISSION.DZ — Synthèse exécutive"
subtitle: "Plateforme SaaS d'aide à la préparation de dossiers de soumission aux marchés publics algériens"
author: "Belhof — Fondateur"
date: "Avril 2026 — Version 5.0"
---

# En bref

**SOUMISSION.DZ** est une plateforme SaaS qui aide les entreprises algériennes à préparer sans erreur leurs dossiers de soumission aux marchés publics. L'outil résout un pain point confirmé par 10 prospects interrogés en présentiel : **ne pas perdre un appel d'offres pour une erreur de processus** (document expiré, pièce manquante, caution oubliée, mauvaise mise en forme).

La v5.0 est une **réécriture complète from scratch** de la v4.0 Lot 1g, menée pour aligner l'architecture sur le modèle produit à 3 cas d'usage validé en avril 2026 (document 09 de cadrage).

# Validation marché

Sur 10 prospects interrogés, **6 sont au niveau d'engagement 3 ou 4** (Lettre d'Intention ou pilote payant). **4 LOI signables** identifiées :

- Brahim (BTPH Sidi Bel Abbès) — Cas 1
- Kamel (BTPH Sétif, 85 employés) — Cas 1
- Mourad (consultant multi-clients) — Cas 2
- Omar (producteur agricole Sud, Ghardaïa) — Cas 1 avec recours ponctuel au Cas 3

# Modèle économique

Six plans tarifaires validés par le marché :

| Plan       | Prix mensuel (DA) | Cible                              |
| ---------- | ----------------- | ---------------------------------- |
| DECOUVERTE | Gratuit (14 j)    | Test                               |
| ARTISAN    | 5 000             | TPE solo                           |
| PRO        | 10 000            | PME 5–30 employés                  |
| BUSINESS   | 15 000            | PME 30+, multi-utilisateurs        |
| EXPERT     | 20 000            | Consultants multi-clients (Cas 2)  |
| HOTLINE    | 4 000             | Add-on support (tous plans)        |

Complément : **mode à l'acte 5 000 DA/dossier**. Service d'assistance Cas 3 à la prestation (catalogue de 7 prestations de 8 000 à 65 000 DA).

# État actuel du produit — v5.0 complète

La v5.0 livre les **9 lots** du mega-prompt de réécriture :

| Lot | Périmètre                                                                 |
| --- | ------------------------------------------------------------------------- |
| 1   | Fondation : modèle 3 tenants, JWT, signup 3 profils, team                 |
| 2   | Coffre-fort (15 types officiels) + références                             |
| 3   | AO + import PDF + audit 25 règles + simulateur 35 prix + templates + DOCX |
| 4   | Kanban dossiers + workflow 3 niveaux + cautions + historique soumissions  |
| 5   | Cabinet Cas 2 : portefeuille N entreprises + comparateur inter-entreprises|
| 6   | Cas 3 assistance : mandat + mission + messagerie + journal + affectation  |
| 7   | Monétisation : plans + abos + factures PDF + parrainage + hotline         |
| 8   | Conformité loi 18-07 : page, consentement, export, soft-delete, purge J+30|
| 9   | Installateur desktop PySide6 (wizard + tray + backup/restore)             |

**Chiffres clés :**

- **~70 endpoints API** protégés par authentification JWT
- **110 tests pytest verts** dont 13+ tests d'isolation cross-tenant
- **4 migrations Alembic** appliquées depuis la base vierge
- **Architecture 3 tenants distincts** : Entreprise autonome, Cabinet multi-entreprises, Plateforme (assistants)
- **Front SPA vanilla JS** sans build step : login, dashboard, coffre, références, AO+audit, chiffrage, kanban, assistance, facturation
- **Installateur PySide6** avec wizard, fenêtre de gestion, system tray, backup/restore ZIP, PyInstaller spec pour `.exe` autonome

Le produit est techniquement **prêt à accueillir les 4 pilotes payants** identifiés.

# Base de démonstration pré-peuplée

Après `python bootstrap.py`, la base simule **2 mois d'activité d'une plateforme en production** :

- 8 entreprises clientes (5 Cas 1 + 3 sous gestion Cabinet Mourad)
- 2 assistants agréés (Yacine BTPH/VRD, Samira fournitures/services)
- **20 appels d'offres** : 12 gagnés / 6 perdus / 2 en cours (≈ 60 % de gain)
- **~615 millions DA** de CA cumulé sur les marchés gagnés
- 102 documents dans les coffres, 33 références historiques
- 32 cautions bancaires actives/récupérées (4 banques : BNA, CPA, BDL, BEA)
- 18 factures SOUMISSION.DZ émises (dont 12 payées)
- 4 missions Cas 3 dans différents états
- 8 tickets hotline, 6 codes de parrainage

Comptes de démonstration fournis : `admin@soumission.dz / Admin12345`, `brahim@alpha-btph.dz / Demo12345`, `mourad@cabinet-mourad.dz / Demo12345`, `yacine.assistant@soumission.dz / Demo12345`, etc.

# Installation

**Option 1 — installateur graphique (pilotes) :** double-clic sur `setup.bat` (Windows) ou `bash setup.sh` (Linux/macOS). Wizard 5 étapes, configuration zero-conf (SQLite, aucun serveur externe), création de l'icône système.

**Option 2 — `.exe` autonome :** `pyinstaller installer/build.spec` produit un binaire ~50 Mo distribuable à un pilote sans Python installé.

**Option 3 — bootstrap CLI (développeurs) :** `python bootstrap.py && uvicorn app.main:app`.

# Différences vs v4.0

| Dimension            | v4.0 Lot 1g           | v5.0                                              |
| -------------------- | --------------------- | ------------------------------------------------- |
| Architecture tenant  | Organisation+Client   | 3 tenants : Entreprise, Cabinet, Plateforme       |
| Cas 2 (consultant)   | Non supporté          | Portefeuille N entreprises + comparateur          |
| Cas 3 (assistance)   | Non supporté          | Module complet mandat + mission + messagerie      |
| Monétisation         | Non implémentée       | 6 plans + factures PDF + parrainage + hotline     |
| Conformité loi 18-07 | Non implémentée       | Page + consentement + export + soft-delete        |
| Migrations           | create_all partiel    | Alembic d'emblée, 4 migrations                    |
| Validation payload   | `data: dict`          | Pydantic 2 sur tous les endpoints                 |
| Front                | Non implémenté        | SPA vanilla JS complète (7 écrans)                |
| Installation pilote  | Manuelle dev          | Installateur desktop + .exe Windows autonome      |
| Base prod            | SQLite                | SQLite par défaut (PostgreSQL optionnel)          |
| Docker               | Requis dev            | **Zéro Docker**                                   |

# Prochaine étape concrète

Le travail de développement v5.0 est **terminé**. Les prochaines étapes sont d'ordre commercial et opérationnel :

1. Signer les 4 LOI identifiées (Brahim, Kamel, Mourad, Omar)
2. Packager l'`.exe` Windows et le distribuer aux 4 pilotes
3. Agréger les retours sur 8-12 semaines d'usage réel
4. Décider de l'hébergement cloud Algérie (Icosnet / Algérie Télécom / Djaweb) quand le volume le justifiera

# Contraintes non-négociables

- Hébergement en **cloud Algérie** (Icosnet, Algérie Télécom ou Djaweb) quand la plateforme passera en mode hébergé (la v5.0 est actuellement en mode pilote local sur poste client)
- **Pas d'IA/LLM** dans la v5.0 (reporté en v6)
- **Pas d'arabe** dans l'interface (0 prospect sur 10 l'a demandé)
- Conformité **loi 18-07** : page `/confidentialite`, consentement horodaté, export ZIP, soft-delete J+30 — tout implémenté
- Fiscalité : mentions NIF / NIS / RC / TVA 19 % — implémenté dans les factures PDF
