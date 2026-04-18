---
title: "SOUMISSION.DZ — Architecture technique v5.0"
subtitle: "Modèle à 3 tenants, couches applicatives, sécurité par construction"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Principes directeurs

- **Monolithe FastAPI** — pas de microservices (prématuré)
- **3 tenants distincts** avec isolation forte (Entreprise, Cabinet, Plateforme)
- **SQLite par défaut, PostgreSQL optionnel** — modèles 100 % portables, zéro `ALTER` spécifique
- **Zéro Docker** — installation native, déployable sur cloud Algérie
- **Front SPA vanilla JS** — pas de build step, pas de node_modules, servi comme static files
- **Sécurité par construction** — `Depends(get_current_context)` obligatoire, scoping automatique, payloads nettoyés

# Couches applicatives

```
┌─────────────────────────────────────────────────┐
│  Static SPA (vanilla JS, 7 écrans)              │
│  static/index.html + app.css + app.js           │
└────────────────┬────────────────────────────────┘
                 │ fetch() + JWT Bearer
┌────────────────▼────────────────────────────────┐
│  FastAPI — 16 routers, ~70 endpoints            │
│  app/routers/*.py                                │
└────────────────┬────────────────────────────────┘
                 │ Depends(get_current_context)
┌────────────────▼────────────────────────────────┐
│  Services métier (pas d'accès direct DB)        │
│  pdf_extractor, rules_engine, catalogue_seed,   │
│  docx_generator                                 │
└────────────────┬────────────────────────────────┘
                 │ ORM
┌────────────────▼────────────────────────────────┐
│  SQLAlchemy 2.x Core + ORM                      │
│  app/models/*.py                                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  SQLite (défaut) ou PostgreSQL 16 (optionnel)   │
└─────────────────────────────────────────────────┘
```

# Modèle à 3 tenants

Les 3 cas d'usage du document 09 se traduisent en 3 types d'organisations, chacune avec sa logique de scoping.

## Cas 1 — Entreprise autonome

```
Organisation (type=ENTREPRISE)
    ↓
Entreprise  (organisation_id)
    ↓
User        (organisation_id, role=PATRON|CHEF_DOSSIER|AUDITEUR)
```

Le scoping est simple : `organisation_id = ctx.org_id`. Filtre direct sur toutes les entités métier.

## Cas 2 — Cabinet multi-entreprises

```
Organisation (type=CABINET)
    ↓
Cabinet     (organisation_id)
    ↓
Entreprise  (cabinet_id=X)   Entreprise (cabinet_id=X)   Entreprise (cabinet_id=X)
    ↓
User        (organisation_id=cabinet.organisation_id, role=CONSULTANT)
```

Le consultant est utilisateur de l'organisation CABINET, mais opère sur des entreprises dont `cabinet_id = cabinet.id`. Le scoping Cas 2 nécessite **le header `X-Entreprise-Active-Id`** pour désigner l'entreprise courante parmi N.

## Cas 3 — Plateforme (assistants agréés)

```
Organisation (type=ENTREPRISE, nom="SOUMISSION.DZ — Assistants")
    ↓
User        (organisation_id, role=ASSISTANT_AGREE)
    ↓
AssistantAgree (user_id, spécialités, IBAN, charte signée)
```

L'assistant n'a **pas d'accès direct** aux entreprises. Il accède uniquement via un **Mandat signé** qui lui donne un périmètre d'actions borné dans le temps sur une entreprise cliente. Chaque action dans le périmètre du mandat est tracée dans `AoMandatAction`.

## Admin plateforme

```
Organisation (type=ENTREPRISE, nom="SOUMISSION.DZ — Admin")
    ↓
User        (organisation_id, role=ADMIN_PLATEFORME)
```

Seul rôle habilité à voir toutes les organisations, recruter des assistants, configurer le catalogue global.

# Scoping : le cœur de la sécurité

Le fichier `app/scoping.py` expose `resolve_entreprise_courante(ctx, db)` qui retourne l'`entreprise_id` de référence selon le profil :

| Profil                          | Logique de résolution                                        |
| ------------------------------- | ------------------------------------------------------------ |
| Cas 1 patron/chef/auditeur      | Première (et unique) entreprise de `ctx.org_id`              |
| Cas 2 consultant                | Entreprise identifiée par `X-Entreprise-Active-Id`, **vérifiée dans le portefeuille du cabinet** |
| Cas 3 assistant                 | Entreprise du mandat actif, **vérifiée dans la base Mandat** |
| Admin plateforme                | Pas de scoping (accès transverse)                            |

**Toute requête qui tenterait un `entreprise_id` hors périmètre retourne `404`** (jamais `403`, pour masquer l'existence même de l'entité).

# 16 routers, ~70 endpoints

| # | Router                  | Responsabilité                                                |
| - | ----------------------- | ------------------------------------------------------------- |
| 1 | `signup.py`             | Création compte entreprise (Cas 1) ou cabinet (Cas 2)         |
| 2 | `auth.py`               | Login JWT, `/me`                                              |
| 3 | `team.py`               | Invitation d'utilisateurs (patron uniquement)                 |
| 4 | `admin.py`              | Recrutement et agrément des assistants Cas 3                  |
| 5 | `coffre.py`             | 15 types officiels de documents, upload/download, alertes expiration |
| 6 | `references.py`         | Historique des marchés précédents                             |
| 7 | `ao.py`                 | CRUD AO, import PDF (extraction regex 48 wilayas), audit 25 règles |
| 8 | `prix.py`               | Catalogue 35 articles BTPH, simulateur de prix avec verdicts  |
| 9 | `templates.py`          | 5 templates de marchés (ROUTES, BATIMENT_PUBLIC, VRD, LPP, HYDRAULIQUE) avec chiffrage proportionnel |
| 10| `memoire.py`            | Génération DOCX mémoire technique + 3 formulaires officiels   |
| 11| `dossiers.py`           | Kanban dossiers 4 colonnes, cautions, historique soumissions  |
| 12| `cabinet.py`            | Portefeuille d'entreprises, comparateur inter-entreprises pour un AO |
| 13| `assistance.py`         | Catalogue 7 prestations, mission Cas 3 (création → validation) |
| 14| `billing.py`            | 6 plans, abonnements mensuels/annuels, factures PDF conformes fiscalité DZ |
| 15| `parrainage_hotline.py` | Codes de parrainage 20 %, tickets hotline 3 niveaux           |
| 16| `conformite.py`         | Page `/confidentialite`, consentement, export ZIP, soft-delete J+30 |

# Modèle de données (8 modules)

```
app/models/
├── base.py         # Base declarative
├── enums.py        # 7 enums : OrgType, OrgStatut, PlanCode, UserRole, ...
├── organisation.py # Table racine tenant (type ENTREPRISE | CABINET)
├── entreprise.py   # NIF, NIS, RC, qualification, wilaya
├── cabinet.py      # Consultant principal, portefeuille
├── user.py         # Email, password_hash, role, last_login
├── metier.py       # Document, Reference, AppelOffres, PrixArticle
├── dossier.py      # Dossier, Caution, Soumission
└── phase4.py       # AssistantAgree, PrestationCatalogue, Mandat, Mission,
                      AoMandatAction, MissionMessage, Plan, Abonnement, Facture,
                      CodeParrainage, Commission, TicketHotline
```

Chaque modèle a :

- `id: int` auto-incrémenté
- `created_at`, `updated_at` avec `default=now()` et `onupdate=now()`
- `deleted_at` pour le soft-delete (sur les entités métier, pas les tables catalogue)

# Alembic — 4 migrations

| # | Migration             | Contenu                                                      |
| - | --------------------- | ------------------------------------------------------------ |
| 1 | `0001_initial.py`     | Organisation, Entreprise, Cabinet, User, enums               |
| 2 | `0002_lots23.py`      | Document, Reference, AppelOffres, PrixArticle                |
| 3 | `0003_phase3.py`      | Dossier, Caution, Soumission                                 |
| 4 | `0004_phase4.py`      | AssistantAgree, Plan, Abonnement, Facture, Mandat, Mission, MissionMessage, AoMandatAction, TicketHotline, CodeParrainage, Commission |

Application : `alembic upgrade head`.

Les migrations sont **SQLite-compatibles** (pas de `ALTER COLUMN` ; on recrée la table si nécessaire). PostgreSQL 16 accepte aussi ce format.

# Services métier

Le dossier `app/services/` ne fait **pas** d'accès base. Il transforme des données pures en objets métier.

## `pdf_extractor.py`

Extraction par regex de champs d'un PDF d'AO uploadé. Champs reconnus : référence, objet, maître d'ouvrage, wilaya (48 wilayas codées), date limite, budget, qualification catégorie.

## `rules_engine.py`

Moteur de 25 règles pondérées avec catégories (documents, qualification, finances, calendrier, cohérence). Score sur 100, verdicts `ok` / `warning` / `danger`, messages français avec suggestion d'action.

## `catalogue_seed.py`

Seeds des 35 articles BTPH (terrassement, gros œuvre, VRD, électricité, plomberie, menuiserie, peinture, étanchéité) et des 5 templates de chiffrage proportionnels.

## `docx_generator.py`

Génération DOCX via `python-docx` du mémoire technique (7 sections) et des 3 formulaires officiels (engagement sur l'honneur, déclaration de probité, liste des références).

# Front SPA

**Pas de build step.** Le frontend est servi par FastAPI en static files depuis `/static/`. Structure minimale :

- `index.html` — login + 7 onglets (Dashboard, Coffre, Références, AO, Chiffrage, Dossiers, Assistance, Facturation)
- `app.css` — 200 lignes, variables CSS couleurs, grid responsive
- `app.js` — 900 lignes, router hash-based, module auth, module API, écrans

Interactions avec l'API via `fetch()` + header `Authorization: Bearer {token}`. Token stocké dans `sessionStorage` (pas de localStorage pour sécurité).

# Installer desktop

Le dossier `installer/` contient :

- `installer_pyside6.py` — application PySide6 (wizard 5 pages + fenêtre principale + system tray)
- `build.spec` — spec PyInstaller pour générer un `.exe` autonome Windows
- `setup.bat` / `setup.sh` — scripts one-click qui créent venv, installent deps, lancent le GUI
- `icon.svg` — icône drapeau algérien

L'installateur exécute `alembic upgrade head`, optionnellement `seeds_demo.py`, puis lance `uvicorn` en sous-processus et ouvre le navigateur sur la SPA.

# Observabilité

**Logs loguru** structurés JSON :

- Stderr en développement
- Fichier rotatif en production (`logs/soumission.log`)
- Niveau configurable via `LOG_LEVEL` dans `.env`
- Champs spéciaux : `user_id`, `org_id`, `entreprise_id` ajoutés par middleware

**Pas de Sentry / Datadog** en v5.0 (à ajouter en v6 si volume le justifie).

# Limitations connues v5.0

- **Pas d'IA/LLM** — aucune suggestion automatique dans les audits (décision D3, reporté v6)
- **Pas de paiement en ligne** — intégration Satim/Edahabia mockée (décision D14, reporté v6 post-pilotes)
- **Pas de notifications push** — alertes visibles uniquement à l'ouverture de l'app
- **SQLite monopostes** — pour multi-utilisateurs simultanés > 10, basculer sur PostgreSQL
- **Pas d'API publique externe** — pas d'intégration comptabilité/ERP tiers
- **Pas de mobile app** — SPA responsive suffit pour la v5.0

# Décisions architecturales clés

Voir `CHANGELOG_v5.md` pour les 40 décisions documentées (D1..D40). Les plus structurantes :

- **D1** Python 3.11+ (StrEnum), pas 3.12 (compatibilité pilotes)
- **D7** Zéro Docker (installation native chez pilote)
- **D11** SQLite par défaut, PostgreSQL optionnel
- **D18** SPA vanilla JS (pas de React) — ROI build tooling négatif pour l'équipe actuelle
- **D23** 3 tenants vs multi-tenant pur — simplicité opérationnelle
- **D31** Installateur PySide6 plutôt qu'Electron — 50 Mo vs 200 Mo, natif cross-platform
