# SOUMISSION.DZ v5.0

Plateforme SaaS d'aide a la preparation et au depot de dossiers de
soumission aux marches publics algeriens. Reecriture from scratch v5.0
basee sur le cadrage produit avril 2026 (3 cas d'usage : entreprise
autonome, consultant multi-entreprises, service d'assistance plateforme).

**Etat : v5.0 complete, 105 tests pytest verts, 9 lots livres, ZERO docker.**

## Stack

- Python 3.11+ + FastAPI + SQLAlchemy 2.x + Alembic + Pydantic 2
- **SQLite par defaut** (zero conf), PostgreSQL optionnel (fichier .env)
- JWT HS256 stdlib + PBKDF2-SHA256 (200k iterations)
- python-docx + reportlab (memoires, formulaires, factures PDF)
- pypdf (extraction AO regex, 48 wilayas)
- loguru (logs JSON loi 18-07)
- PySide6 (installateur desktop optionnel)
- **Frontend SPA vanilla JS** (no build step, no React, ~700 lignes)

## Installation — 3 options

### Option 1 — Installateur graphique (RECOMMANDE pour pilotes non-tech)

**Windows** :
```cmd
installer\setup.bat
```

**Linux / macOS** :
```bash
bash installer/setup.sh
```

Le script :
1. Verifie Python 3.11+
2. Cree un environnement virtuel `.venv`
3. Installe toutes les dependances (y compris PySide6)
4. Lance l'installateur graphique

L'installateur graphique propose un **wizard 5 etapes** (Bienvenue → Verification prerequis avec auto-install des composants manquants → Configuration zero-conf → Installation → Terminé), puis ouvre la **fenetre principale** avec 4 onglets :
- **Statut** : Demarrer / Arreter / Redemarrer + logs en temps reel + ouvrir le navigateur
- **Sauvegardes** : backup ZIP (DB + storage + .env) + restauration en 1 clic
- **Parametres** : port d'ecoute, chemin DB/storage, re-injection des donnees demo
- **A propos** : version + conformite + info architecture

L'application reste accessible dans la **barre systeme** (system tray) meme si la fenetre est fermee.

### Option 2 — Empaquetage en .exe Windows autonome

```bash
pip install pyinstaller
pyinstaller installer/build.spec
# Sortie : dist/soumission-dz/soumission-dz.exe (~50 Mo, autonome, sans Python a installer)
```

Le `.exe` peut etre distribue tel quel a un pilote qui n'a meme pas Python.

### Option 3 — Bootstrap CLI (pour developpeurs)

```bash
pip install fastapi 'sqlalchemy>=2.0' alembic 'pydantic>=2' pydantic-settings \
            python-multipart loguru python-docx pypdf reportlab email-validator uvicorn

python bootstrap.py     # cree .env + DB SQLite + migrations + seeds demo
uvicorn app.main:app    # ouvre http://127.0.0.1:8000
```

### Option 4 — Mode headless (serveur Linux sans GUI)

```bash
python installer/installer_pyside6.py --headless
```

Detecte un port libre, applique les migrations et lance uvicorn. Ctrl+C pour arreter.

---
## Comptes de demonstration

Apres `bootstrap.py` ou clic sur "Charger donnees demo" dans l'installateur :


| Email | Mot de passe | Cas |
|-------|-------------|-----|
| `admin@soumission.dz` | `Admin12345` | Admin plateforme |
| `brahim@alpha-btph.dz` | `Demo12345` | Cas 1 entreprise (Sidi Bel Abbes) — donnees pre-remplies |
| `kamel@batipro-setif.dz` | `Demo12345` | Cas 1 entreprise (Setif) |
| `amine@hydra-etudes.dz` | `Demo12345` | Cas 1 entreprise (Alger, etudes) |
| `nadia@omega-fournitures.dz` | `Demo12345` | Cas 1 entreprise (Oran, fournitures) |
| `omar@sud-travaux.dz` | `Demo12345` | Cas 1 entreprise (Ghardaia, services) |
| `mourad@cabinet-mourad.dz` | `Demo12345` | Cas 2 cabinet consultant |
| `yacine.assistant@soumission.dz` | `Demo12345` | Cas 3 assistant agree (BTPH, VRD) |
| `samira.assistant@soumission.dz` | `Demo12345` | Cas 3 assistant agree (fournitures, services) |

## Installateur desktop optionnel

```bash
pip install PySide6
python installer/installer_pyside6.py
```

Fenetre graphique avec boutons Demarrer / Arreter / Redemarrer /
Charger demo / Verifier prerequis / Ouvrir le navigateur.

## Reset complet

```bash
python bootstrap.py --reset       # supprime DB + storage et recommence
python bootstrap.py --no-seeds    # init sans seeds demo
```

## Tests (105 verts)

```bash
pytest -v
```

```
tests/test_signup.py    : 6   tests
tests/test_auth.py      : 8   tests   (G1 token expire)
tests/test_isolation.py : 5   tests   (G2/G3 cross-tenant)
tests/test_team.py      : 4   tests
tests/test_phase2.py    : 26  tests   (Lots 2+3 — coffre/refs/ao/audit/prix/templates/memoire/formulaires)
tests/test_phase3.py    : 18  tests   (Lots 4+5 — kanban/cautions/historique/cabinet)
tests/test_phase4.py    : 14  tests   (Lot 6 — Cas 3 mandat/mission/journal/messagerie)
tests/test_phase5.py    : 20  tests   (Lots 7+8 — billing/parrainage/hotline/loi 18-07)
tests/test_installer.py : 4   tests   (Lot 9 — installateur PySide6 helpers)
                         ===
                         105 verts
```

## Frontend SPA

Le frontend (`/static/index.html` + `app.css` + `app.js`) est une SPA
vanilla JS sans build :

- Login + signup entreprise + signup cabinet
- Dashboard avec KPIs (docs, alertes expiration, refs, AO, factures)
- Coffre-fort : upload PDF, list, download, delete
- References : CRUD complet
- AO : CRUD + import-PDF avec extraction regex + audit 25 regles avec
  affichage couleur OK/warning/danger + generation memoire DOCX
- Kanban dossiers (4 colonnes a_faire / en_cours / a_valider / termine)
- Facturation : plans, abonnements, factures PDF, paiement mock

Ouvrir simplement `http://127.0.0.1:8000` apres le `uvicorn`.

## Endpoints API (~70 routes)

Voir `/docs` (Swagger UI auto-genere par FastAPI) pour la liste complete
et tester chaque endpoint.

## Securite (contrat verifie par 13+ tests d'isolation)

1. `Depends(get_current_context)` sur tous les endpoints metier
2. Filtrage par entreprise_id (Cas 1) ou cabinet_id+entreprise_active_id (Cas 2)
3. Payload nettoye : organisation_id/cabinet_id ECRASES par ctx serveur
4. Cross-tenant -> 404 (G2, jamais 403, masque l'existence)
5. Token expire/falsifie -> 401 (G1)
6. Action assistant sans mandat valide -> 403 + log AoMandatAction
7. Tests d'isolation cross-tenant OBLIGATOIRES par endpoint metier

## Structure

```
soumission_dz/
  bootstrap.py                Script init zero-conf
  .env.example                Template (SQLite par defaut)
  pyproject.toml              Deps + pytest config
  alembic.ini, alembic/       4 migrations (0001 a 0004)
  app/
    main.py, config.py, database.py, security.py, deps.py, scoping.py
    seeds_demo.py             5 entreprises + cabinet + 2 assistants + AO demo
    models/                   8 modules (organisation, entreprise, cabinet,
                                user, metier, dossier, phase4, enums)
    schemas/                  Pydantic 2 schemas par domaine
    routers/                  16 routers (auth, signup, team, admin, coffre,
                                references, ao, prix, templates, memoire,
                                dossiers, cabinet, assistance, billing,
                                parrainage_hotline, conformite)
    services/                 4 services (pdf_extractor, rules_engine,
                                catalogue_seed, docx_generator)
  static/
    index.html, app.css, app.js     Frontend SPA vanilla JS
  installer/
    installer_pyside6.py      Installateur desktop sans docker
  tests/                      9 fichiers, 105 tests
  storage/                    Fichiers uploades (entreprise_id/type/file)
  CHANGELOG_v5.md             Historique + 40 decisions documentees
```

## Hebergement production

Pour mise en prod chez Icosnet / Algerie Telecom / Djaweb :

```bash
# Sur le serveur prod
git clone <repo> && cd soumission_dz
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # ou les deps listees plus haut

# .env prod (SQLite suffit < 50 entreprises ; sinon Postgres natif)
cat > .env <<EOF
SOUMISSION_ENV=production
SOUMISSION_JWT_SECRET=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///./soumission_dz.db
STORAGE_ROOT=/var/soumission_dz/storage
LOG_LEVEL=INFO
EOF

alembic upgrade head
gunicorn -k uvicorn.workers.UvicornWorker -w 4 app.main:app -b 127.0.0.1:8000
# nginx reverse proxy + TLS Let's Encrypt
```

Aucune dependance Docker. Postgres optionnel uniquement si volume eleve.

Voir `CHANGELOG_v5.md` pour les 40 decisions techniques documentees (D1..D40)
et le detail de chaque lot.
