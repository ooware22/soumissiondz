# -*- coding: utf-8 -*-
"""SOUMISSION.DZ — Installateur desktop (Lot 9, sans Docker).

Application desktop tout-en-un :

  - Wizard premier demarrage : verification prerequis, install auto des deps
    pip manquantes, generation du .env, application des migrations,
    chargement optionnel des donnees de demonstration
  - Fenetre principale post-install : statut serveur, logs en temps reel,
    backup/restore de la base, parametres, page A propos
  - Icone systeme (system tray) avec menu contextuel
  - Detection automatique d'un port libre si 8000 occupe
  - Icone custom + theme algerien

Lancement :
  python installer/installer_pyside6.py            # lance le wizard si premier run, sinon la main window
  python installer/installer_pyside6.py --reset    # force le wizard meme si .env existe
  python installer/installer_pyside6.py --headless # mode CLI (verifications + uvicorn, sans GUI)

Empaquetage Windows .exe :
  pip install pyinstaller
  pyinstaller installer/build.spec

Sortie : dist/soumission-dz/soumission-dz.exe (~50 Mo, autonome).
"""
from __future__ import annotations

import argparse
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path

# --- Imports differes : PySide6 peut etre absent au moment du check, on l'install
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    QT_AVAILABLE = True
except ImportError:
    QtCore = QtGui = QtWidgets = None  # type: ignore
    QT_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
DB_FILE = PROJECT_ROOT / "soumission_dz.db"
STORAGE_DIR = PROJECT_ROOT / "storage"
ICON_FILE = Path(__file__).resolve().parent / "icon.svg"
APP_NAME = "SOUMISSION.DZ"
APP_VERSION = "5.0.0"


# =============================================================================
# Helpers metier (testables sans PySide6)
# =============================================================================

REQUIRED_DEPS = [
    "fastapi", "uvicorn", "sqlalchemy", "alembic", "pydantic",
    "pydantic_settings", "loguru", "docx", "pypdf", "reportlab",
    "multipart", "email_validator",
]
PIP_NAMES = {  # mapping module -> nom pypi
    "docx": "python-docx",
    "multipart": "python-multipart",
    "email_validator": "email-validator",
    "pydantic_settings": "pydantic-settings",
}


MIN_PYTHON = (3, 11)


def python_version_ok() -> tuple[bool, str]:
    v = sys.version_info
    ok = (v.major, v.minor) >= MIN_PYTHON
    return ok, f"Python {v.major}.{v.minor}.{v.micro}"


def deps_python_ok() -> tuple[bool, list[str]]:
    """Verifie quels modules sont manquants. Renvoie (ok, missing_module_names)."""
    missing = []
    for mod in REQUIRED_DEPS:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    return len(missing) == 0, missing


def deps_to_pip_args(missing: list[str]) -> list[str]:
    """Convertit les noms de modules en arguments pip (avec mapping pypi)."""
    return [PIP_NAMES.get(m, m) for m in missing]


def find_free_port(start: int = 8000, end: int = 8050) -> int:
    """Trouve le premier port TCP libre entre start et end. Defaut 8000."""
    for p in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return start  # fallback


def generer_env_si_absent(port: int = 8000) -> bool:
    """Cree .env zero-conf SQLite avec JWT_SECRET cryptographique."""
    if ENV_FILE.exists():
        return False
    secret = secrets.token_hex(32)
    ENV_FILE.write_text(
        f"SOUMISSION_ENV=production\n"
        f"SOUMISSION_JWT_SECRET={secret}\n"
        f"SOUMISSION_JWT_EXPIRE_HOURS=24\n"
        f"DATABASE_URL=sqlite:///{DB_FILE.as_posix()}\n"
        f"STORAGE_ROOT={STORAGE_DIR.as_posix()}\n"
        f"LOG_LEVEL=INFO\n"
        f"SOUMISSION_PORT={port}\n",
        encoding="utf-8",
    )
    return True


def first_run() -> bool:
    """True si la plateforme n'a jamais ete installee sur ce poste."""
    return not ENV_FILE.exists() or not DB_FILE.exists()


def _env_for_subprocess() -> dict:
    env = os.environ.copy()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def backup_to_zip(dest: Path) -> Path:
    """Sauvegarde DB SQLite + storage/ + .env dans un .zip horodate."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        if DB_FILE.exists():
            zf.write(DB_FILE, arcname="soumission_dz.db")
        if ENV_FILE.exists():
            zf.write(ENV_FILE, arcname=".env")
        if STORAGE_DIR.exists():
            for p in STORAGE_DIR.rglob("*"):
                if p.is_file() and p.name != ".gitkeep":
                    zf.write(p, arcname=str(p.relative_to(PROJECT_ROOT)))
    return dest


def restore_from_zip(src: Path) -> tuple[bool, str]:
    """Restaure depuis un .zip cree par backup_to_zip. Retourne (ok, message)."""
    if not src.exists():
        return False, "Fichier de sauvegarde introuvable."
    try:
        # Sauvegarde defensive de l'etat courant
        if DB_FILE.exists():
            DB_FILE.rename(DB_FILE.with_suffix(".db.bak"))
        with zipfile.ZipFile(src, "r") as zf:
            zf.extractall(PROJECT_ROOT)
        return True, f"Restauration depuis {src.name} reussie."
    except Exception as e:
        # Rollback
        bak = DB_FILE.with_suffix(".db.bak")
        if bak.exists():
            bak.rename(DB_FILE)
        return False, f"Echec restauration : {e}"


# =============================================================================
# ServiceManager — alembic + uvicorn (zero docker)
# =============================================================================
class ServiceManager:
    def __init__(self, log_callback=None, port: int = 8000):
        self.uvicorn_proc: subprocess.Popen | None = None
        self.log = log_callback or (lambda m: print(m))
        self.port = port

    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def alembic_upgrade(self) -> bool:
        try:
            r = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=PROJECT_ROOT, env=_env_for_subprocess(),
                capture_output=True, text=True, timeout=60,
            )
            if r.stdout: self.log(r.stdout.strip())
            if r.stderr: self.log(r.stderr.strip())
            return r.returncode == 0
        except Exception as e:
            self.log(f"[ERREUR alembic] {e}")
            return False

    def seeds_demo(self) -> bool:
        try:
            r = subprocess.run(
                [sys.executable, "-m", "app.seeds_demo"],
                cwd=PROJECT_ROOT, env=_env_for_subprocess(),
                capture_output=True, text=True, timeout=60,
            )
            if r.stdout: self.log(r.stdout.strip())
            if r.stderr: self.log(r.stderr.strip())
            return r.returncode == 0
        except Exception as e:
            self.log(f"[ERREUR seeds] {e}")
            return False

    def install_missing_deps(self, modules: list[str]) -> bool:
        """Installe via pip les paquets manquants. Renvoie True si tout OK."""
        if not modules:
            return True
        pkgs = deps_to_pip_args(modules)
        self.log(f"[PIP] Installation : {' '.join(pkgs)}")
        try:
            r = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", *pkgs],
                capture_output=True, text=True, timeout=300,
            )
            if r.stdout: self.log(r.stdout.strip())
            if r.stderr: self.log(r.stderr.strip())
            return r.returncode == 0
        except Exception as e:
            self.log(f"[ERREUR pip] {e}")
            return False

    def uvicorn_start(self) -> bool:
        if self.uvicorn_proc and self.uvicorn_proc.poll() is None:
            self.log("[INFO] Serveur deja en cours.")
            return True
        try:
            self.uvicorn_proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app",
                 "--host", "127.0.0.1", "--port", str(self.port)],
                cwd=PROJECT_ROOT, env=_env_for_subprocess(),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            threading.Thread(target=self._stream_logs, daemon=True).start()
            time.sleep(2)
            self.log(f"[OK] Serveur demarre sur {self.url()}")
            return True
        except Exception as e:
            self.log(f"[ERREUR uvicorn] {e}")
            return False

    def uvicorn_stop(self) -> None:
        if self.uvicorn_proc and self.uvicorn_proc.poll() is None:
            try:
                self.uvicorn_proc.send_signal(signal.SIGTERM)
                self.uvicorn_proc.wait(timeout=10)
            except Exception:
                self.uvicorn_proc.kill()
            self.log("[INFO] Serveur arrete.")
        self.uvicorn_proc = None

    def _stream_logs(self) -> None:
        if not self.uvicorn_proc or not self.uvicorn_proc.stdout:
            return
        for line in self.uvicorn_proc.stdout:
            self.log(line.rstrip())

    def is_running(self) -> bool:
        return self.uvicorn_proc is not None and self.uvicorn_proc.poll() is None


# =============================================================================
# UI — Wizard premier demarrage (5 pages)
# =============================================================================
def _build_wizard():
    from PySide6 import QtCore, QtGui, QtWidgets

    QWP = QtWidgets.QWizardPage

    PRIMARY = "#0b5394"
    PRIMARY_DARK = "#073763"
    BG = "#f7f9fc"

    class WelcomePage(QWP):
        def __init__(self):
            super().__init__()
            self.setTitle("Bienvenue sur SOUMISSION.DZ")
            self.setSubTitle("Plateforme SaaS pour vos soumissions aux marches publics algeriens.")
            l = QtWidgets.QVBoxLayout(self)
            l.addWidget(QtWidgets.QLabel(
                "<p>Cet assistant va installer SOUMISSION.DZ sur votre poste en quelques etapes :</p>"
                "<ol style='line-height:1.8'>"
                "<li>Verification des prerequis</li>"
                "<li>Installation automatique des composants manquants</li>"
                "<li>Configuration zero (SQLite, aucun serveur externe)</li>"
                "<li>Donnees de demonstration optionnelles</li>"
                "<li>Lancement</li>"
                "</ol>"
                "<p style='color:#6b7280'>Cliquez sur <b>Suivant</b> pour commencer.</p>"
            ))

    class CheckPage(QWP):
        def __init__(self):
            super().__init__()
            self.setTitle("Verification des prerequis")
            self.setSubTitle("L'assistant verifie votre poste et installe ce qui manque automatiquement.")
            l = QtWidgets.QVBoxLayout(self)
            self.list = QtWidgets.QPlainTextEdit()
            self.list.setReadOnly(True)
            self.list.setStyleSheet("font-family:Menlo,Consolas,monospace; padding:8px;")
            l.addWidget(self.list)
            self.btn_install = QtWidgets.QPushButton("Installer les composants manquants")
            self.btn_install.clicked.connect(self._install_missing)
            l.addWidget(self.btn_install)
            self._all_ok = False

        def initializePage(self) -> None:
            self.list.clear()
            self._check()

        def _check(self) -> None:
            self.list.appendPlainText("--- Verification en cours ---")
            ok_py, ver = python_version_ok()
            self.list.appendPlainText(
                f"[{'OK' if ok_py else 'KO'}] {ver} {'(>= 3.11 requis)' if not ok_py else ''}"
            )
            ok_dp, miss = deps_python_ok()
            if ok_dp:
                self.list.appendPlainText("[OK] Toutes les dependances Python sont installees")
                self._all_ok = ok_py
                self.btn_install.hide()
            else:
                self.list.appendPlainText(
                    f"[!]  Composants manquants ({len(miss)}) : {', '.join(deps_to_pip_args(miss))}"
                )
                self.list.appendPlainText("    Cliquez sur le bouton ci-dessous pour les installer.")
                self._all_ok = False
                self.btn_install.show()
            self.completeChanged.emit()

        def _install_missing(self) -> None:
            _ok, miss = deps_python_ok()
            if not miss:
                return
            self.btn_install.setEnabled(False)
            self.btn_install.setText("Installation en cours, patientez…")
            QtWidgets.QApplication.processEvents()
            svc = ServiceManager(log_callback=lambda m: self.list.appendPlainText(m))
            ok = svc.install_missing_deps(miss)
            if ok:
                self.list.appendPlainText("[OK] Installation reussie")
                self._all_ok = True
                self.btn_install.hide()
            else:
                self.list.appendPlainText("[KO] Installation echouee, verifiez votre connexion.")
                self.btn_install.setEnabled(True)
                self.btn_install.setText("Reessayer")
            self.completeChanged.emit()

        def isComplete(self) -> bool:
            return self._all_ok

    class ConfigPage(QWP):
        def __init__(self):
            super().__init__()
            self.setTitle("Configuration")
            self.setSubTitle("Zero configuration : tout est pret a fonctionner.")
            l = QtWidgets.QVBoxLayout(self)
            self.summary = QtWidgets.QLabel()
            self.summary.setWordWrap(True)
            self.summary.setStyleSheet(
                "background:#fff;padding:14px;border:1px solid #e5e7eb;border-radius:6px;"
            )
            l.addWidget(self.summary)

            l.addWidget(QtWidgets.QLabel(""))
            self.cb_seeds = QtWidgets.QCheckBox(
                "Charger les donnees de demonstration (5 entreprises, 1 cabinet, 2 assistants, "
                "1 AO et son audit)"
            )
            self.cb_seeds.setChecked(True)
            l.addWidget(self.cb_seeds)
            self.registerField("load_seeds", self.cb_seeds)

            # Champ cache pour le port (QLineEdit = support natif QWizard.field)
            self._port_field = QtWidgets.QLineEdit()
            self._port_field.hide()
            l.addWidget(self._port_field)
            self.registerField("port", self._port_field)

        def initializePage(self) -> None:
            port = find_free_port()
            self._port_field.setText(str(port))
            self.summary.setText(
                f"<b>Base de donnees :</b> SQLite (fichier local, aucun serveur).<br>"
                f"<b>Fichier :</b> {DB_FILE}<br>"
                f"<b>Stockage :</b> {STORAGE_DIR}<br>"
                f"<b>Port :</b> {port} (auto-detecte)<br>"
                f"<b>JWT_SECRET :</b> sera genere aleatoirement (256 bits)"
            )

    class InstallPage(QWP):
        def __init__(self):
            super().__init__()
            self.setTitle("Installation en cours")
            self.setSubTitle("Generation des fichiers et application des migrations.")
            l = QtWidgets.QVBoxLayout(self)
            self.progress = QtWidgets.QProgressBar()
            self.progress.setRange(0, 100)
            l.addWidget(self.progress)
            self.logs = QtWidgets.QPlainTextEdit()
            self.logs.setReadOnly(True)
            self.logs.setStyleSheet(
                "background:#1e1e1e;color:#0f0;font-family:Menlo,Consolas,monospace;padding:8px;"
            )
            l.addWidget(self.logs)
            self._done = False

        def initializePage(self) -> None:
            self.progress.setValue(0)
            self.logs.clear()
            QtCore.QTimer.singleShot(100, self._run)

        def _run(self) -> None:
            port_str = self.field("port") or ""
            try:
                port = int(str(port_str)) if port_str else find_free_port()
            except (ValueError, TypeError):
                port = find_free_port()
            self._log(f"[1/4] Generation du fichier .env (port {port})…")
            generer_env_si_absent(port=port)
            self.progress.setValue(25)
            QtWidgets.QApplication.processEvents()

            self._log("[2/4] Creation du dossier de stockage…")
            STORAGE_DIR.mkdir(exist_ok=True)
            (STORAGE_DIR / ".gitkeep").touch()
            self.progress.setValue(40)
            QtWidgets.QApplication.processEvents()

            self._log("[3/4] Application des migrations Alembic…")
            svc = ServiceManager(log_callback=self._log, port=port)
            if not svc.alembic_upgrade():
                self._log("[ERREUR] Echec des migrations.")
                return
            self.progress.setValue(70)
            QtWidgets.QApplication.processEvents()

            if self.field("load_seeds"):
                self._log("[4/4] Insertion des donnees de demonstration…")
                if not svc.seeds_demo():
                    self._log("[ATTENTION] Seeds en echec, mais l'installation continue.")
            else:
                self._log("[4/4] Skip seeds (demande utilisateur).")

            self.progress.setValue(100)
            self._log("\n=== Installation terminee avec succes ! ===")
            self._done = True
            self.completeChanged.emit()

        def _log(self, msg: str) -> None:
            self.logs.appendPlainText(msg)
            self.logs.verticalScrollBar().setValue(self.logs.verticalScrollBar().maximum())

        def isComplete(self) -> bool:
            return self._done

    class DonePage(QWP):
        def __init__(self):
            super().__init__()
            self.setTitle("Installation terminee")
            self.setSubTitle("SOUMISSION.DZ est pret a l'emploi.")
            l = QtWidgets.QVBoxLayout(self)
            self.label = QtWidgets.QLabel()
            self.label.setWordWrap(True)
            l.addWidget(self.label)
            self.cb_launch = QtWidgets.QCheckBox(
                "Demarrer maintenant le serveur et ouvrir le navigateur"
            )
            self.cb_launch.setChecked(True)
            l.addWidget(self.cb_launch)
            self.registerField("launch_now", self.cb_launch)

        def initializePage(self) -> None:
            seeds = bool(self.field("load_seeds"))
            seed_block = ""
            if seeds:
                seed_block = (
                    "<p><b>Comptes de demonstration disponibles</b> (mot de passe <code>Demo12345</code>):</p>"
                    "<ul style='line-height:1.6'>"
                    "<li><b>brahim@alpha-btph.dz</b> — Cas 1, Sidi Bel Abbes (donnees pre-remplies)</li>"
                    "<li><b>mourad@cabinet-mourad.dz</b> — Cas 2 cabinet</li>"
                    "<li><b>admin@soumission.dz</b> / <b>Admin12345</b> — administrateur</li>"
                    "</ul>"
                )
            self.label.setText(
                f"<p>Tout est en place. Vous pouvez maintenant utiliser SOUMISSION.DZ.</p>"
                f"{seed_block}"
                f"<p style='color:#6b7280'>Vous retrouverez l'application dans la "
                f"<b>fenetre de gestion</b> et dans la <b>barre systeme</b>.</p>"
            )

    class SetupWizard(QtWidgets.QWizard):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(f"Installateur {APP_NAME} v{APP_VERSION}")
            self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
            self.setMinimumSize(720, 540)
            self.setOption(QtWidgets.QWizard.NoBackButtonOnStartPage, True)
            # Boutons en francais
            self.setButtonText(QtWidgets.QWizard.NextButton, "Suivant >")
            self.setButtonText(QtWidgets.QWizard.BackButton, "< Precedent")
            self.setButtonText(QtWidgets.QWizard.CancelButton, "Annuler")
            self.setButtonText(QtWidgets.QWizard.FinishButton, "Terminer")

            self.addPage(WelcomePage())
            self.addPage(CheckPage())
            self.addPage(ConfigPage())
            self.addPage(InstallPage())
            self.addPage(DonePage())

            self.setStyleSheet(
                f"QWizard {{ background:{BG}; }}"
                f"QPushButton {{ background:{PRIMARY}; color:white; padding:6px 14px; "
                f"border-radius:4px; border:0; }}"
                f"QPushButton:hover {{ background:{PRIMARY_DARK}; }}"
                f"QPushButton:disabled {{ background:#ccc; color:#666; }}"
            )

    return SetupWizard


# =============================================================================
# UI — Main window post-install (4 onglets : Statut, Backup, Parametres, A propos)
# =============================================================================
def _build_main_window():
    from PySide6 import QtCore, QtGui, QtWidgets

    PRIMARY = "#0b5394"
    PRIMARY_DARK = "#073763"

    class StatutTab(QtWidgets.QWidget):
        def __init__(self, mw):
            super().__init__()
            self.mw = mw
            l = QtWidgets.QVBoxLayout(self)

            self.status_label = QtWidgets.QLabel()
            self.status_label.setStyleSheet("font-size:14px; padding:8px;")
            l.addWidget(self.status_label)

            row = QtWidgets.QHBoxLayout()
            self.btn_start = QtWidgets.QPushButton("▶  Demarrer")
            self.btn_stop = QtWidgets.QPushButton("■  Arreter")
            self.btn_restart = QtWidgets.QPushButton("⟳  Redemarrer")
            self.btn_open = QtWidgets.QPushButton("🌐  Ouvrir le navigateur")
            for b in (self.btn_start, self.btn_stop, self.btn_restart, self.btn_open):
                row.addWidget(b)
            l.addLayout(row)

            self.url_label = QtWidgets.QLabel()
            self.url_label.setOpenExternalLinks(True)
            l.addWidget(self.url_label)

            self.logs = QtWidgets.QPlainTextEdit()
            self.logs.setReadOnly(True)
            self.logs.setStyleSheet(
                "background:#1e1e1e;color:#0f0;"
                "font-family:Menlo,Consolas,monospace;padding:8px;"
            )
            l.addWidget(self.logs, 1)

            row2 = QtWidgets.QHBoxLayout()
            row2.addWidget(QtWidgets.QLabel("Logs :"))
            row2.addStretch()
            self.btn_clear_logs = QtWidgets.QPushButton("Effacer")
            self.btn_clear_logs.clicked.connect(self.logs.clear)
            row2.addWidget(self.btn_clear_logs)
            l.addLayout(row2)

            self.btn_start.clicked.connect(self.mw.do_start)
            self.btn_stop.clicked.connect(self.mw.do_stop)
            self.btn_restart.clicked.connect(self.mw.do_restart)
            self.btn_open.clicked.connect(self.mw.do_open_browser)

        def append_log(self, msg: str) -> None:
            QtCore.QMetaObject.invokeMethod(
                self.logs, "appendPlainText",
                QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, str(msg)),
            )

        def refresh(self, running: bool, url: str) -> None:
            if running:
                self.status_label.setText(
                    "<b style='color:#2e7d32; font-size:18px'>● En marche</b>"
                )
                self.url_label.setText(
                    f"Acces : <a href='{url}'>{url}</a>"
                )
            else:
                self.status_label.setText(
                    "<b style='color:#b91c1c; font-size:18px'>● Arrete</b>"
                )
                self.url_label.setText("")
            self.btn_start.setEnabled(not running)
            self.btn_stop.setEnabled(running)
            self.btn_restart.setEnabled(running)
            self.btn_open.setEnabled(running)

    class BackupTab(QtWidgets.QWidget):
        def __init__(self, mw):
            super().__init__()
            self.mw = mw
            l = QtWidgets.QVBoxLayout(self)

            l.addWidget(QtWidgets.QLabel(
                "<h3>Sauvegarde et restauration</h3>"
                "<p>Sauvegarde la base SQLite + tous les documents uploades dans un fichier ZIP unique. "
                "Restauration possible sur ce poste ou un autre poste.</p>"
            ))

            row = QtWidgets.QHBoxLayout()
            self.btn_backup = QtWidgets.QPushButton("💾  Sauvegarder maintenant")
            self.btn_restore = QtWidgets.QPushButton("📥  Restaurer depuis un ZIP…")
            row.addWidget(self.btn_backup)
            row.addWidget(self.btn_restore)
            row.addStretch()
            l.addLayout(row)

            l.addWidget(QtWidgets.QLabel("<b>Sauvegardes existantes :</b>"))
            self.list = QtWidgets.QListWidget()
            l.addWidget(self.list, 1)

            self.btn_backup.clicked.connect(self._backup)
            self.btn_restore.clicked.connect(self._restore)

            self._refresh()

        def _backup_dir(self) -> Path:
            d = PROJECT_ROOT / "backups"
            d.mkdir(exist_ok=True)
            return d

        def _refresh(self) -> None:
            self.list.clear()
            d = self._backup_dir()
            for f in sorted(d.glob("*.zip"), reverse=True):
                kb = f.stat().st_size // 1024
                self.list.addItem(f"{f.name}   ({kb} Ko)")

        def _backup(self) -> None:
            self.mw.do_stop()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = self._backup_dir() / f"backup_{ts}.zip"
            backup_to_zip(dest)
            QtWidgets.QMessageBox.information(
                self, "Sauvegarde", f"Sauvegarde creee :\n{dest}"
            )
            self._refresh()

        def _restore(self) -> None:
            f, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Choisir un fichier de sauvegarde",
                str(self._backup_dir()), "ZIP (*.zip)",
            )
            if not f:
                return
            confirm = QtWidgets.QMessageBox.question(
                self, "Confirmation",
                "ATTENTION : la restauration ecrasera la base actuelle.\n"
                "Une copie de securite sera conservee en .db.bak.\n\nContinuer ?",
            )
            if confirm != QtWidgets.QMessageBox.Yes:
                return
            self.mw.do_stop()
            ok, msg = restore_from_zip(Path(f))
            QtWidgets.QMessageBox.information(self, "Restauration", msg)
            if ok:
                self._refresh()

    class ParamsTab(QtWidgets.QWidget):
        def __init__(self, mw):
            super().__init__()
            self.mw = mw
            l = QtWidgets.QFormLayout(self)
            self.port_input = QtWidgets.QSpinBox()
            self.port_input.setRange(1024, 65535)
            self.port_input.setValue(mw.svc.port)
            l.addRow("Port d'ecoute :", self.port_input)

            self.path_db = QtWidgets.QLineEdit(str(DB_FILE))
            self.path_db.setReadOnly(True)
            l.addRow("Base SQLite :", self.path_db)

            self.path_storage = QtWidgets.QLineEdit(str(STORAGE_DIR))
            self.path_storage.setReadOnly(True)
            l.addRow("Stockage :", self.path_storage)

            self.btn_apply = QtWidgets.QPushButton("Appliquer (necessite redemarrage)")
            self.btn_apply.clicked.connect(self._apply)
            l.addRow("", self.btn_apply)

            self.btn_open_dir = QtWidgets.QPushButton("Ouvrir le dossier de l'application")
            self.btn_open_dir.clicked.connect(
                lambda: webbrowser.open(f"file://{PROJECT_ROOT}")
            )
            l.addRow("", self.btn_open_dir)

            self.btn_reset_demo = QtWidgets.QPushButton(
                "🔄 Reinjecter les donnees de demo (idempotent)"
            )
            self.btn_reset_demo.clicked.connect(self._reseed)
            l.addRow("", self.btn_reset_demo)

        def _apply(self) -> None:
            self.mw.svc.port = self.port_input.value()
            # Met a jour le .env
            if ENV_FILE.exists():
                lines = ENV_FILE.read_text().splitlines()
                new = []
                seen = False
                for line in lines:
                    if line.startswith("SOUMISSION_PORT="):
                        new.append(f"SOUMISSION_PORT={self.port_input.value()}")
                        seen = True
                    else:
                        new.append(line)
                if not seen:
                    new.append(f"SOUMISSION_PORT={self.port_input.value()}")
                ENV_FILE.write_text("\n".join(new) + "\n")
            QtWidgets.QMessageBox.information(
                self, "Parametres",
                f"Port mis a jour : {self.port_input.value()}.\nRedemarrez le serveur."
            )

        def _reseed(self) -> None:
            self.mw.svc.seeds_demo()
            QtWidgets.QMessageBox.information(
                self, "Donnees de demo",
                "Les seeds ont ete re-executes (operation idempotente)."
            )

    class AboutTab(QtWidgets.QWidget):
        def __init__(self, _mw):
            super().__init__()
            l = QtWidgets.QVBoxLayout(self)
            l.setAlignment(QtCore.Qt.AlignTop)
            l.addWidget(QtWidgets.QLabel(
                f"<h2 style='color:{PRIMARY}'>SOUMISSION.DZ</h2>"
                f"<p><b>Version</b> {APP_VERSION}</p>"
                "<p>Plateforme SaaS d'aide a la preparation et au depot de "
                "dossiers de soumission aux marches publics algeriens.</p>"
                "<p><b>Conformite :</b> loi 18-07 (export des donnees, soft-delete + purge J+30, "
                "logs structures).</p>"
                "<p><b>Fiscalite :</b> factures NIF/NIS/RC + TVA 19%.</p>"
                "<p><b>Securite :</b> JWT HS256, PBKDF2-SHA256 200k iterations, isolation "
                "cross-tenant verifiee par 13+ tests automatises.</p>"
                "<hr>"
                "<p style='color:#6b7280'>Architecture : Python 3.11+ + FastAPI + SQLAlchemy 2.x + "
                "SQLite (zero docker, zero serveur externe).</p>"
                "<p style='color:#6b7280'>Frontend : SPA vanilla JS, sans build.</p>"
                "<p style='color:#6b7280'>Hebergement recommande prod : cloud Algerie "
                "(Icosnet, Algerie Telecom, Djaweb).</p>"
            ))

    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} — Gestion locale")
            self.resize(900, 640)

            port = find_free_port()
            self.svc = ServiceManager(log_callback=self._on_log, port=port)

            tabs = QtWidgets.QTabWidget()
            self.statut_tab = StatutTab(self)
            self.backup_tab = BackupTab(self)
            self.params_tab = ParamsTab(self)
            self.about_tab = AboutTab(self)
            tabs.addTab(self.statut_tab, "📊  Statut")
            tabs.addTab(self.backup_tab, "💾  Sauvegardes")
            tabs.addTab(self.params_tab, "⚙  Parametres")
            tabs.addTab(self.about_tab, "ℹ  A propos")
            self.setCentralWidget(tabs)

            # Status bar
            self.statusBar().showMessage(
                f"Pret. Cliquez sur Demarrer pour lancer le serveur sur le port {port}."
            )

            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self._refresh_status)
            self.timer.start(1500)

            # System tray
            self._setup_tray()

            self.statut_tab.refresh(False, self.svc.url())

        def _on_log(self, msg: str) -> None:
            self.statut_tab.append_log(msg)

        def _refresh_status(self) -> None:
            running = self.svc.is_running()
            self.statut_tab.refresh(running, self.svc.url())
            self.tray_action_status.setText(
                f"Serveur : {'En marche' if running else 'Arrete'}"
            )

        def do_start(self) -> None:
            if not self.svc.alembic_upgrade():
                QtWidgets.QMessageBox.critical(
                    self, "Erreur", "Echec des migrations Alembic. Voir les logs."
                )
                return
            self.svc.uvicorn_start()
            self._refresh_status()

        def do_stop(self) -> None:
            self.svc.uvicorn_stop()
            self._refresh_status()

        def do_restart(self) -> None:
            self.do_stop()
            time.sleep(1)
            self.do_start()

        def do_open_browser(self) -> None:
            webbrowser.open(self.svc.url())

        def _setup_tray(self) -> None:
            icon = self._load_icon()
            self.tray = QtWidgets.QSystemTrayIcon(icon, self)
            menu = QtWidgets.QMenu()
            self.tray_action_status = menu.addAction("Serveur : Arrete")
            self.tray_action_status.setEnabled(False)
            menu.addSeparator()
            menu.addAction("Demarrer", self.do_start)
            menu.addAction("Arreter", self.do_stop)
            menu.addAction("Ouvrir le navigateur", self.do_open_browser)
            menu.addSeparator()
            menu.addAction("Afficher la fenetre", self.show_normal)
            menu.addAction("Quitter", self._quit)
            self.tray.setContextMenu(menu)
            self.tray.setToolTip(APP_NAME)
            self.tray.activated.connect(self._tray_activated)
            self.tray.show()

        def _tray_activated(self, reason) -> None:
            if reason == QtWidgets.QSystemTrayIcon.Trigger:
                self.show_normal()

        def _load_icon(self) -> QtGui.QIcon:
            if ICON_FILE.exists():
                return QtGui.QIcon(str(ICON_FILE))
            # Fallback : icone genere a la volee
            pix = QtGui.QPixmap(64, 64)
            pix.fill(QtGui.QColor(PRIMARY))
            return QtGui.QIcon(pix)

        def show_normal(self) -> None:
            self.show()
            self.activateWindow()
            self.raise_()

        def _quit(self) -> None:
            self.svc.uvicorn_stop()
            QtWidgets.QApplication.quit()

        def closeEvent(self, ev) -> None:
            # Minimise dans le tray plutot que de quitter
            if self.tray and self.tray.isVisible():
                ev.ignore()
                self.hide()
                self.tray.showMessage(
                    APP_NAME,
                    "L'application continue de tourner en arriere-plan.",
                    QtWidgets.QSystemTrayIcon.Information,
                    3000,
                )
            else:
                self.svc.uvicorn_stop()
                super().closeEvent(ev)

    return MainWindow


# =============================================================================
# Mode headless (CLI sans GUI)
# =============================================================================
def headless_run() -> int:
    print(f"{APP_NAME} v{APP_VERSION} — mode headless")
    ok_py, ver = python_version_ok()
    print(f"  {ver} : {'OK' if ok_py else 'KO (>=3.11 requis)'}")
    if not ok_py:
        return 1
    ok_dp, miss = deps_python_ok()
    if not ok_dp:
        print(f"  Composants manquants : {deps_to_pip_args(miss)}")
        print("  Installez avec : pip install " + " ".join(deps_to_pip_args(miss)))
        return 1
    port = find_free_port()
    generer_env_si_absent(port=port)
    STORAGE_DIR.mkdir(exist_ok=True)
    svc = ServiceManager(log_callback=print, port=port)
    if not svc.alembic_upgrade():
        return 1
    svc.uvicorn_start()
    print(f"\nServeur en marche sur {svc.url()}")
    print("Ctrl+C pour arreter.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        svc.uvicorn_stop()
    return 0


# =============================================================================
# Entree principale
# =============================================================================
def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--reset", action="store_true",
                   help="Force le wizard meme si .env existe")
    p.add_argument("--headless", action="store_true",
                   help="Mode CLI sans GUI (pour serveur Linux)")
    args = p.parse_args()

    if args.headless:
        return headless_run()

    if not QT_AVAILABLE:
        print("ERREUR : PySide6 n'est pas installe.")
        print("  Installation rapide :  pip install PySide6")
        print("  Ou utilisation sans GUI :  python installer/installer_pyside6.py --headless")
        return 1

    # Note : pas de `from PySide6 import ...` ici — on utilise l'import global
    # (sinon Python marque QtWidgets comme local dans main() et ca shadow le
    # symbole global, provoquant UnboundLocalError sur les premieres references)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)

    if first_run() or args.reset:
        if args.reset and DB_FILE.exists():
            DB_FILE.unlink()
        if args.reset and ENV_FILE.exists():
            ENV_FILE.unlink()
        Wizard = _build_wizard()
        wiz = Wizard()
        result = wiz.exec()
        if result != QtWidgets.QDialog.Accepted:
            return 0
        # Laisser le wizard terminer puis ouvrir la main window
        if wiz.field("launch_now"):
            MainWindow = _build_main_window()
            mw = MainWindow()
            mw.show()
            mw.do_start()
            return app.exec()
        return 0
    else:
        MainWindow = _build_main_window()
        mw = MainWindow()
        mw.show()
        return app.exec()


if __name__ == "__main__":
    sys.exit(main())
