---
title: "SOUMISSION.DZ — Déploiement"
subtitle: "Modes pilote local, serveur dédié, cloud Algérie"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Trois modes de déploiement

La v5.0 supporte 3 modes selon la maturité commerciale :

1. **Pilote local** — poste client Windows/Linux (.exe ou setup.bat)
2. **Serveur dédié interne** — un VPS chez un pilote volumineux (30+ utilisateurs)
3. **Cloud Algérie hébergé** — Icosnet, Algérie Télécom, Djaweb (quand le volume justifie)

**Aucun Docker requis dans les 3 modes.**

# Mode 1 — Pilote local

## Cas d'usage

- 4 pilotes signés (Brahim, Kamel, Mourad, Omar)
- Usage mono-poste ou multi-poste sur même LAN
- SQLite suffit (< 50 entreprises, < 20 utilisateurs simultanés)
- Pas d'accès Internet requis (hors signup/mise à jour)

## Distribution

Option A — `.exe` Windows autonome :

```bash
# Côté développeur
pip install pyinstaller
pyinstaller installer/build.spec
# Produit : dist/soumission-dz/soumission-dz.exe (~50 Mo)
# À signer avec un certificat code signing (évite alerte SmartScreen)
```

Le pilote reçoit le `.exe` par email / WeTransfer / clé USB, double-clique, le wizard démarre.

Option B — Scripts setup (Linux ou dev) :

```bash
unzip soumission-dz-v5.0.zip
cd soumission_dz
bash installer/setup.sh         # ou setup.bat sous Windows
```

## Architecture

```
┌─────────────────────────────────────┐
│  Poste Windows/Linux du pilote      │
│  ┌───────────────────────────────┐  │
│  │ installer_pyside6.py (GUI)    │  │
│  │  ├─ System tray icon          │  │
│  │  └─ Fenêtre de gestion        │  │
│  └───────────┬───────────────────┘  │
│              │ subprocess            │
│  ┌───────────▼───────────────────┐  │
│  │ uvicorn 127.0.0.1:8000        │  │
│  │  ├─ FastAPI app               │  │
│  │  └─ SQLite local              │  │
│  └───────────┬───────────────────┘  │
│              │ HTTP                  │
│  ┌───────────▼───────────────────┐  │
│  │ Navigateur (Chrome/Edge/FF)   │  │
│  │ http://127.0.0.1:8000         │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Fichiers produits chez le pilote

```
C:\Users\Brahim\SOUMISSION.DZ\
├── .env                         # JWT_SECRET unique, généré au 1er lancement
├── soumission_dz.db             # Base SQLite
├── storage/                     # Documents PDF uploadés
│   └── 1/documents/             # Par entreprise_id
├── backups/                     # Backups ZIP générés depuis le GUI
├── logs/                        # Logs loguru
└── soumission-dz.exe            # L'exécutable lui-même
```

## Sauvegardes

L'installateur offre un onglet "Sauvegardes" qui :

- Crée un ZIP horodaté contenant DB + storage + .env
- Restaure depuis un ZIP précédent en 1 clic (avec confirmation)

Recommandation : configurer un script Windows Task Scheduler quotidien qui copie `backups/backup_YYYYMMDD_HHMMSS.zip` sur un NAS ou OneDrive.

## Mise à jour

- Le pilote télécharge la nouvelle version du `.exe`
- Au lancement, l'installateur détecte qu'il y a déjà un `.env`/DB
- Applique `alembic upgrade head` automatiquement
- Les données sont préservées

## Multi-poste LAN

Pour 2-10 postes sur le même réseau local :

- Installer sur un poste "serveur" (celui qui reste allumé)
- Modifier `.env` : `SOUMISSION_HOST=0.0.0.0` (accepter connexions LAN)
- Firewall Windows : autoriser le port 8000 en entrée
- Autres postes : naviguent vers `http://<IP_SERVEUR>:8000`

SQLite gère bien jusqu'à ~10 connexions concurrentes. Au-delà, passer au mode 2.

# Mode 2 — Serveur dédié interne

## Cas d'usage

- Un pilote avec > 30 utilisateurs (Batipro Sétif, Kamel, 85 employés)
- Volume de dossiers élevé justifiant PostgreSQL
- Besoin d'accès depuis plusieurs agences

## Infrastructure cible

- 1 VPS Linux (Ubuntu 22.04 ou 24.04) chez Icosnet ou Algérie Télécom
- 2 vCPU, 4 Go RAM, 80 Go SSD
- PostgreSQL 16 installé nativement
- Nginx + certbot Let's Encrypt
- Gunicorn pour servir FastAPI

## Installation

```bash
# 1. Préparer le serveur
sudo apt update && sudo apt install -y python3.11 python3.11-venv \
    python3-pip postgresql-16 nginx certbot python3-certbot-nginx

# 2. Base de données
sudo -u postgres psql <<EOF
CREATE USER soumission WITH PASSWORD '<MOT_DE_PASSE_FORT>';
CREATE DATABASE soumission_dz OWNER soumission;
EOF

# 3. Application
cd /opt
git clone <repo> soumission_dz
cd soumission_dz
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg[binary]

# 4. Configuration
cat > .env <<EOF
SOUMISSION_ENV=production
SOUMISSION_JWT_SECRET=$(openssl rand -hex 32)
DATABASE_URL=postgresql+psycopg://soumission:<MOT_DE_PASSE_FORT>@localhost:5432/soumission_dz
STORAGE_ROOT=/var/soumission_dz/storage
LOG_LEVEL=INFO
EOF

# 5. Migrations
alembic upgrade head

# 6. Service systemd
sudo tee /etc/systemd/system/soumission-dz.service > /dev/null <<EOF
[Unit]
Description=SOUMISSION.DZ FastAPI
After=network.target postgresql.service

[Service]
Type=simple
User=soumission
WorkingDirectory=/opt/soumission_dz
Environment="PATH=/opt/soumission_dz/.venv/bin"
EnvironmentFile=/opt/soumission_dz/.env
ExecStart=/opt/soumission_dz/.venv/bin/gunicorn \\
    -k uvicorn.workers.UvicornWorker -w 4 \\
    -b 127.0.0.1:8000 app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now soumission-dz

# 7. Nginx reverse proxy
sudo tee /etc/nginx/sites-available/soumission-dz > /dev/null <<'EOF'
server {
    listen 80;
    server_name app.exemple-pilote.dz;

    client_max_body_size 25M;    # Uploads PDF jusqu'à 25 Mo

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
sudo ln -s /etc/nginx/sites-available/soumission-dz /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 8. TLS Let's Encrypt
sudo certbot --nginx -d app.exemple-pilote.dz
```

## Backup automatisé

```bash
# /etc/cron.daily/soumission-backup
#!/bin/bash
set -e
STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/var/backups/soumission_dz
mkdir -p $BACKUP_DIR

# Dump PostgreSQL
sudo -u postgres pg_dump soumission_dz | gzip > $BACKUP_DIR/db_$STAMP.sql.gz

# Tar storage
tar -czf $BACKUP_DIR/storage_$STAMP.tar.gz -C /var/soumission_dz storage/

# Rétention : garder 30 jours
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

# Mode 3 — Cloud Algérie hébergé

## Cas d'usage

- Passage en SaaS multi-tenant après succès des 4 pilotes
- Volume anticipé : 50-500 entreprises clientes
- Besoin d'exploitation professionnelle (monitoring, SLA, support 24/7)

## Choix du fournisseur

Trois options, toutes en territoire algérien (conformité loi 18-07) :

| Fournisseur        | Avantages                          | Inconvénients                    |
| ------------------ | ---------------------------------- | -------------------------------- |
| **Icosnet**        | Expérience avec SaaS DZ            | Coût élevé                       |
| **Algérie Télécom**| Infrastructure nationale, scale OK | Bureaucratie pour contrats       |
| **Djaweb**         | Bon rapport qualité/prix           | Moins d'options premium          |

Critère **non-négociable** : datacenter physiquement en Algérie, contrat mentionnant la localisation.

## Architecture cible

```
┌──────────────────────────────────────────────────────────┐
│  Cloud Algérie (Icosnet/AT/Djaweb)                       │
│                                                          │
│  ┌─────────────────────┐   ┌──────────────────────────┐ │
│  │ Nginx + Let's Encrypt│   │ PostgreSQL 16 (managed)  │ │
│  │ app.soumission.dz    │   │ Sauvegardes auto         │ │
│  └──────────┬──────────┘   └──────────────────────────┘ │
│             │                          ▲                 │
│  ┌──────────▼──────────┐              │                 │
│  │ Gunicorn + 4 workers │              │                 │
│  │ soumission_dz app    │──────────────┘                 │
│  └──────────┬──────────┘                                 │
│             │                                             │
│  ┌──────────▼──────────┐                                 │
│  │ Object storage       │                                 │
│  │ (documents PDF)      │                                 │
│  └─────────────────────┘                                 │
└──────────────────────────────────────────────────────────┘
```

## Mesures v6 à prévoir

- Passage de `storage/` local à un object storage Algérie (à identifier)
- Mise en place Sentry ou alternative DZ pour monitoring erreurs
- Métriques Prometheus + Grafana pour capacity planning
- CI/CD (GitHub Actions ou Gitlab selon contrat)
- Plan de reprise d'activité (PRA) : réplication PostgreSQL sur datacenter secondaire

# Variables d'environnement

Toutes déclarées dans `.env` (template : `.env.example`) :

| Variable                     | Défaut                       | Description                           |
| ---------------------------- | ---------------------------- | ------------------------------------- |
| `SOUMISSION_ENV`             | `development`                | `production` active les protections   |
| `SOUMISSION_JWT_SECRET`      | (obligatoire)                | 256 bits, généré aléatoirement        |
| `SOUMISSION_JWT_EXPIRE_HOURS`| `24`                         | Durée de vie des tokens JWT           |
| `DATABASE_URL`               | `sqlite:///./soumission_dz.db` | PostgreSQL via `postgresql+psycopg://...` |
| `STORAGE_ROOT`               | `./storage`                  | Racine des uploads                    |
| `LOG_LEVEL`                  | `INFO`                       | `DEBUG`/`WARNING`/`ERROR`             |
| `SOUMISSION_PORT`            | `8000`                       | Port HTTP d'écoute                    |

En production, `SOUMISSION_ENV=production` :

- Désactive `/docs` (Swagger)
- Désactive les tracebacks détaillés dans les réponses
- Active les logs JSON strictement structurés

# Monitoring minimal

- `GET /health` — retourne `{"status": "ok", "version": "5.0"}`
- Appel régulier par un script externe (cron, UptimeRobot, Pingdom)
- Alerte email ou Slack si la réponse n'est pas 200 pendant 3 minutes

En v6, ajouter :

- Métriques applicatives : nombre de signups, AOs créés, missions validées, factures émises par jour
- Métriques infra : CPU, RAM, disque, latence P50/P95/P99

# Sécurité déploiement

- Jamais de secrets dans le code Git
- `.env` en dehors du repo, chmod 600
- HTTPS obligatoire (HTTP redirigé en 301)
- Headers sécurité Nginx : `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`
- Firewall : seuls 22 (SSH), 80 (redirect), 443 (HTTPS) ouverts
- SSH clé uniquement, pas de mot de passe
- Utilisateur système dédié `soumission` (pas root)

# Rollback

- Sauvegardes DB quotidiennes chiffrées
- Sauvegardes storage (incrémental rsync ou borgbackup)
- Procédure documentée : `scripts/rollback.sh <BACKUP_TIMESTAMP>`
- Tester le rollback **au moins une fois par mois** sur environnement staging
