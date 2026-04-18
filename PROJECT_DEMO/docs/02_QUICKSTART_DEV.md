---
title: "SOUMISSION.DZ — Guide de démarrage développeur"
subtitle: "Installation, configuration, premier lancement, tests"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Prérequis

- **Python 3.11 ou 3.12** (3.11.7 validé)
- **pip** (fourni avec Python)
- **Aucun Docker requis**
- **Aucun PostgreSQL requis** (SQLite par défaut ; PostgreSQL optionnel pour volume > 50 entreprises)

Vérifier la version Python :

```bash
python --version    # ou python3 --version
```

# Installation en 3 options

## Option 1 — Installateur graphique (recommandé pour pilotes)

**Windows :**

```cmd
installer\setup.bat
```

**Linux / macOS :**

```bash
bash installer/setup.sh
```

Le script :

1. Vérifie Python 3.11+
2. Crée un environnement virtuel `.venv`
3. Installe toutes les dépendances, y compris PySide6
4. Lance l'installateur graphique (wizard 5 étapes + fenêtre de gestion)

## Option 2 — Bootstrap CLI (développeurs)

```bash
# 1. Dépendances
pip install fastapi 'sqlalchemy>=2.0' alembic 'pydantic>=2' pydantic-settings \
            python-multipart loguru python-docx pypdf reportlab \
            email-validator uvicorn

# 2. Init zero-conf (crée .env + DB SQLite + migrations + seeds démo)
python bootstrap.py

# 3. Lancer le serveur
uvicorn app.main:app --reload --port 8000
```

Ouvre <http://127.0.0.1:8000> dans le navigateur.

## Option 3 — .exe Windows autonome

Pour distribuer à un pilote sans Python installé :

```bash
pip install pyinstaller
pyinstaller installer/build.spec
# Sortie : dist/soumission-dz/soumission-dz.exe (~50 Mo, autonome)
```

# Comptes de démonstration

Après `bootstrap.py`, la base contient 2 mois d'activité simulée :

| Email                              | Mot de passe | Rôle / contexte                |
| ---------------------------------- | ------------ | ------------------------------ |
| `admin@soumission.dz`              | `Admin12345` | Admin plateforme               |
| `brahim@alpha-btph.dz`             | `Demo12345`  | Cas 1 — Alpha BTPH (SBA)       |
| `kamel@batipro-setif.dz`           | `Demo12345`  | Cas 1 — Batipro (Sétif)        |
| `amine@hydra-etudes.dz`            | `Demo12345`  | Cas 1 — Hydra Études (Alger)   |
| `nadia@omega-fournitures.dz`       | `Demo12345`  | Cas 1 — Omega (Oran)           |
| `omar@sud-travaux.dz`              | `Demo12345`  | Cas 1 — Sud Travaux (Ghardaïa) |
| `mourad@cabinet-mourad.dz`         | `Demo12345`  | Cas 2 — Cabinet (3 entrepises) |
| `yacine.assistant@soumission.dz`   | `Demo12345`  | Cas 3 — Assistant BTPH/VRD     |
| `samira.assistant@soumission.dz`   | `Demo12345`  | Cas 3 — Assistant Fournitures  |

# Structure du projet

```
soumission_dz/
├── bootstrap.py                    # Script init zero-conf
├── .env.example                    # Template (SQLite par défaut)
├── pyproject.toml                  # Deps + pytest + ruff config
├── alembic.ini, alembic/           # 4 migrations (0001..0004)
├── app/
│   ├── main.py                     # Factory FastAPI + lifespan + static /
│   ├── config.py                   # pydantic-settings (.env → Settings)
│   ├── database.py                 # engine + SessionLocal + get_db
│   ├── security.py                 # PBKDF2-SHA256 + JWT HS256 stdlib
│   ├── deps.py                     # get_current_context + require_patron + require_admin
│   ├── scoping.py                  # resolve_entreprise_courante (Cas 1 + Cas 2)
│   ├── seeds_demo.py               # Scénario 2 mois : 20 AO + 12 gagnés + ...
│   ├── models/                     # 8 modules (base, enums, organisation, entreprise,
│   │                                cabinet, user, metier, dossier, phase4)
│   ├── schemas/                    # Schémas Pydantic 2 par domaine
│   ├── routers/                    # 16 routers (voir ci-dessous)
│   └── services/                   # pdf_extractor, rules_engine, catalogue_seed,
│                                     docx_generator
├── static/
│   ├── index.html                  # SPA 7 onglets
│   ├── app.css, app.js             # ~900 lignes vanilla JS
├── installer/
│   ├── installer_pyside6.py        # Wizard + fenêtre principale + tray
│   ├── build.spec                  # PyInstaller .exe
│   ├── setup.bat, setup.sh         # One-click pour pilotes
│   └── icon.svg                    # Icône custom drapeau algérien
├── tests/                          # 9 fichiers, 110 tests
├── storage/                        # Fichiers uploadés
└── CHANGELOG_v5.md                 # 40 décisions documentées (D1..D40)
```

# Les 16 routers

| Router                   | Endpoints principaux                                  |
| ------------------------ | ----------------------------------------------------- |
| `signup.py`              | `/signup/entreprise`, `/signup/cabinet`               |
| `auth.py`                | `/auth/login`, `/auth/me`                             |
| `team.py`                | `/team`, `/team/invite` (patron uniquement)           |
| `admin.py`               | `/admin/assistants` (recrutement Cas 3)               |
| `coffre.py`              | `/coffre/types`, `/coffre/documents/*`, `/coffre/alertes` |
| `references.py`          | `/references` CRUD                                    |
| `ao.py`                  | `/ao` CRUD + `/import-pdf` + `/{id}/audit`            |
| `prix.py`                | `/prix/articles`, `/prix/simuler`                     |
| `templates.py`           | `/templates`, `/templates/{code}/chiffrer`            |
| `memoire.py`             | `/memoire/generer`, `/formulaires/{code}/generer`     |
| `dossiers.py`            | `/dossiers` + kanban + cautions + soumissions         |
| `cabinet.py`             | `/cabinet/entreprises`, `/cabinet/comparer`           |
| `assistance.py`          | `/assistance/prestations`, `/missions/*` (Cas 3)      |
| `billing.py`             | `/plans`, `/abonnements`, `/factures/*`               |
| `parrainage_hotline.py`  | `/parrainage/*`, `/hotline/*`                         |
| `conformite.py`          | `/confidentialite/*` (loi 18-07)                      |

# Tests (110 verts)

```bash
pytest -v
```

```
tests/test_signup.py    :  6 tests
tests/test_auth.py      :  8 tests    (G1 token expiré)
tests/test_isolation.py :  5 tests    (G2/G3 cross-tenant)
tests/test_team.py      :  4 tests
tests/test_phase2.py    : 26 tests    (Lots 2+3)
tests/test_phase3.py    : 18 tests    (Lots 4+5)
tests/test_phase4.py    : 14 tests    (Lot 6 Cas 3)
tests/test_phase5.py    : 20 tests    (Lots 7+8)
tests/test_installer.py :  9 tests    (Lot 9)
                         ===
                         110 verts
```

# Linting

```bash
ruff check app/ tests/
ruff format app/ tests/
mypy app/       # optionnel
```

# Reset complet

```bash
python bootstrap.py --reset       # supprime DB + storage et recommence
python bootstrap.py --no-seeds    # init sans données démo (base vierge)
```

# Développement

- **Ajouter un endpoint métier** : toujours avec `Depends(get_current_context)` + filtrage scoping (voir `app/scoping.py`). Ajouter un test d'isolation cross-tenant obligatoirement.
- **Ajouter un modèle** : créer dans `app/models/`, importer dans `app/models/__init__.py`, créer la migration Alembic (`alembic revision --autogenerate -m "..."`), appliquer avec `alembic upgrade head`.
- **Ajouter un champ sur un modèle existant** : migration Alembic incrémentale (`alembic revision --autogenerate`), relire le diff, appliquer.
- **Mettre à jour les seeds** : éditer `app/seeds_demo.py` (idempotent), relancer `python -m app.seeds_demo` ou `bootstrap.py --reset`.

# Debug

- Logs loguru structurés JSON en stderr. Niveau via `LOG_LEVEL` dans `.env`.
- Swagger UI auto-généré sur <http://127.0.0.1:8000/docs>.
- Base SQLite consultable avec `sqlite3 soumission_dz.db` ou avec DB Browser for SQLite.

# Passage en production

Le mode pilote v5.0 est conçu pour tourner localement chez le client. Pour un hébergement cloud Algérie (Icosnet / Algérie Télécom / Djaweb), voir le document 05 déploiement.

Changement principal en prod : basculer `DATABASE_URL` vers PostgreSQL 16 (installation native), remplacer `uvicorn --reload` par `gunicorn` + nginx reverse proxy + TLS Let's Encrypt.
