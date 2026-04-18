# -*- coding: utf-8 -*-
"""Bootstrap SOUMISSION.DZ — zero conf, zero docker.

Usage:
    python bootstrap.py            # init complet : .env + DB + migrations + seeds
    python bootstrap.py --reset    # supprime tout et recommence
    python bootstrap.py --no-seeds # init sans donnees de demo

Apres bootstrap : `uvicorn app.main:app --reload --port 8000`
"""
from __future__ import annotations

import argparse
import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
DB_FILE = ROOT / "soumission_dz.db"
STORAGE_DIR = ROOT / "storage"


def info(msg: str) -> None:
    print(f"[bootstrap] {msg}")


def step_env() -> None:
    if ENV_FILE.exists():
        info(".env deja present, on conserve.")
        return
    secret = secrets.token_hex(32)
    ENV_FILE.write_text(
        f"SOUMISSION_ENV=production\n"
        f"SOUMISSION_JWT_SECRET={secret}\n"
        f"SOUMISSION_JWT_EXPIRE_HOURS=24\n"
        f"DATABASE_URL=sqlite:///{DB_FILE.as_posix()}\n"
        f"STORAGE_ROOT={STORAGE_DIR.as_posix()}\n"
        f"LOG_LEVEL=INFO\n",
        encoding="utf-8",
    )
    info(f".env genere avec JWT_SECRET cryptographique fort.")


def step_storage() -> None:
    STORAGE_DIR.mkdir(exist_ok=True)
    (STORAGE_DIR / ".gitkeep").touch()
    info(f"storage/ pret : {STORAGE_DIR}")


def step_migrations() -> None:
    info("Application des migrations Alembic…")
    env = os.environ.copy()
    # Charge le .env qu'on vient de creer
    for line in ENV_FILE.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    if r.returncode != 0:
        info(f"ERREUR alembic :\n{r.stdout}\n{r.stderr}")
        sys.exit(1)
    info("Schema DB a jour.")


def step_seeds() -> None:
    info("Insertion des donnees de demonstration…")
    env = os.environ.copy()
    for line in ENV_FILE.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    r = subprocess.run(
        [sys.executable, "-m", "app.seeds_demo"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    print(r.stdout)
    if r.returncode != 0:
        info(f"ERREUR seeds :\n{r.stderr}")
        sys.exit(1)


def step_reset() -> None:
    info("Reset complet…")
    if DB_FILE.exists():
        DB_FILE.unlink()
        info(f"  - DB supprimee : {DB_FILE.name}")
    if STORAGE_DIR.exists():
        import shutil
        for child in STORAGE_DIR.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        info(f"  - storage/ vide")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--reset", action="store_true", help="Supprime DB + storage")
    p.add_argument("--no-seeds", action="store_true", help="Skip seeds de demo")
    args = p.parse_args()

    info(f"Project root : {ROOT}")
    if args.reset:
        step_reset()
    step_env()
    step_storage()
    step_migrations()
    if not args.no_seeds:
        step_seeds()

    info("=" * 60)
    info("Bootstrap termine.")
    info("Lancer le serveur : uvicorn app.main:app --reload --port 8000")
    info("Ou via l'installateur GUI : python installer/installer_pyside6.py")
    info("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
