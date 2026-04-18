#!/usr/bin/env bash
# SOUMISSION.DZ - Setup Linux/macOS one-click

set -e
cd "$(dirname "$0")/.."

echo "============================================================"
echo " SOUMISSION.DZ - Installation"
echo "============================================================"

# Verifier Python 3.11+
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] Python 3 n'est pas installe."
    echo "Linux Debian/Ubuntu : sudo apt install python3.11 python3.11-venv"
    echo "macOS              : brew install python@3.11"
    exit 1
fi

PYV=$(python3 --version | awk '{print $2}')
echo "Python detecte : $PYV"

# Creer venv si absent
if [ ! -d .venv ]; then
    echo "Creation de l'environnement virtuel .venv ..."
    python3 -m venv .venv
fi

# Activer venv
# shellcheck disable=SC1091
source .venv/bin/activate

# Installer deps
echo "Installation des dependances Python ..."
python -m pip install --upgrade pip --quiet
python -m pip install --quiet \
    fastapi "sqlalchemy>=2.0" alembic "pydantic>=2" pydantic-settings \
    python-multipart loguru python-docx pypdf reportlab email-validator \
    uvicorn

# PySide6 optionnel (peut echouer sur certains Linux server)
if python -m pip install --quiet PySide6 2>/dev/null; then
    echo "[OK] PySide6 installe (mode GUI disponible)"
    HAS_GUI=1
else
    echo "[INFO] PySide6 non installe (mode headless seulement)"
    HAS_GUI=0
fi

echo
echo "============================================================"

if [ "$HAS_GUI" = "1" ] && [ -n "$DISPLAY" ]; then
    echo " Lancement de l'installateur graphique"
    echo "============================================================"
    python installer/installer_pyside6.py
else
    echo " Lancement en mode headless (pas d'affichage detecte)"
    echo "============================================================"
    python installer/installer_pyside6.py --headless
fi
