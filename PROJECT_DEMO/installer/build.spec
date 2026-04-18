# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — empaquette l'installateur en .exe Windows ou binaire Linux/macOS.

Build :
    pip install pyinstaller
    pyinstaller installer/build.spec

Sortie :
    dist/soumission-dz/soumission-dz.exe        (Windows)
    dist/soumission-dz/soumission-dz            (Linux/macOS)

Le binaire est autonome (~50 Mo). Au lancement :
- Si .env absent : ouvre le wizard d'installation
- Sinon : ouvre la fenetre principale
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Racine projet (le spec est dans installer/)
ROOT = os.path.dirname(os.path.abspath(SPEC))
PROJECT = os.path.dirname(ROOT)

# Tout embarquer pour un binaire autonome
datas = [
    (os.path.join(PROJECT, "app"),       "app"),
    (os.path.join(PROJECT, "alembic"),   "alembic"),
    (os.path.join(PROJECT, "alembic.ini"), "."),
    (os.path.join(PROJECT, "static"),    "static"),
    (os.path.join(PROJECT, "installer", "icon.svg"), "installer"),
]
datas += collect_data_files("alembic")
datas += collect_data_files("docx", include_py_files=False)

hiddenimports = []
hiddenimports += collect_submodules("app")
hiddenimports += collect_submodules("alembic")
hiddenimports += collect_submodules("sqlalchemy")
hiddenimports += [
    "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
    "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets", "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan", "uvicorn.lifespan.on",
    "psycopg",  # support optionnel postgres
    "passlib.handlers.pbkdf2",
    "email_validator",
]

a = Analysis(
    [os.path.join(ROOT, "installer_pyside6.py")],
    pathex=[PROJECT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "notebook"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="soumission-dz",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # GUI app (pas de console)
    disable_windowed_traceback=False,
    icon=os.path.join(ROOT, "icon.svg") if os.path.exists(os.path.join(ROOT, "icon.svg")) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="soumission-dz",
)
