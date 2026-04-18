@echo off
REM SOUMISSION.DZ - Setup Windows one-click
REM Verifie Python, cree un venv, installe les deps et lance l'installateur GUI

setlocal
cd /d "%~dp0\.."

echo ============================================================
echo  SOUMISSION.DZ - Installation
echo ============================================================
echo.

REM Verifier Python 3.11+
where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo Telechargez Python 3.11+ sur https://www.python.org/downloads/
    echo Pendant l'installation cochez "Add Python to PATH".
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%V in ('python --version 2^>^&1') do set PYV=%%V
echo Python detecte : %PYV%

REM Creer venv si absent
if not exist .venv (
    echo Creation de l'environnement virtuel .venv ...
    python -m venv .venv
)

REM Activer venv
call .venv\Scripts\activate.bat

REM Installer deps
echo Installation des dependances Python ...
python -m pip install --upgrade pip --quiet
python -m pip install --quiet ^
    fastapi "sqlalchemy>=2.0" alembic "pydantic>=2" pydantic-settings ^
    python-multipart loguru python-docx pypdf reportlab email-validator ^
    uvicorn PySide6

if errorlevel 1 (
    echo [ERREUR] Echec d'installation des dependances.
    pause
    exit /b 1
)

REM Lancer l'installateur GUI
echo.
echo ============================================================
echo  Lancement de l'installateur graphique
echo ============================================================
python installer\installer_pyside6.py

endlocal
