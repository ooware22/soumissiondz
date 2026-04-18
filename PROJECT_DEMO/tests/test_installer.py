# -*- coding: utf-8 -*-
"""Tests pour les helpers de l'installateur (sans PySide6 ni GUI)."""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

# Ajoute installer/ au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "installer"))


def test_python_version_ok():
    from installer_pyside6 import python_version_ok
    ok, ver = python_version_ok()
    assert ok is True
    assert ver.startswith("Python 3.")


def test_deps_python_essentiels():
    from installer_pyside6 import deps_python_ok
    _ok, missing = deps_python_ok()
    essential = {"fastapi", "sqlalchemy", "alembic", "pydantic", "loguru",
                 "docx", "pypdf", "reportlab"}
    assert essential.isdisjoint(set(missing)), f"Manquants essentiels: {essential & set(missing)}"


def test_deps_to_pip_args_mapping():
    from installer_pyside6 import deps_to_pip_args
    args = deps_to_pip_args(["docx", "multipart", "fastapi"])
    assert "python-docx" in args
    assert "python-multipart" in args
    assert "fastapi" in args


def test_find_free_port():
    from installer_pyside6 import find_free_port
    port = find_free_port(start=18000, end=18050)
    assert 18000 <= port <= 18050


def test_generer_env(tmp_path, monkeypatch):
    import installer_pyside6 as inst
    fake_env = tmp_path / ".env"
    fake_db = tmp_path / "soumission_dz.db"
    fake_storage = tmp_path / "storage"
    monkeypatch.setattr(inst, "ENV_FILE", fake_env)
    monkeypatch.setattr(inst, "DB_FILE", fake_db)
    monkeypatch.setattr(inst, "STORAGE_DIR", fake_storage)
    assert inst.generer_env_si_absent(port=8042) is True
    content = fake_env.read_text()
    assert "SOUMISSION_JWT_SECRET=" in content
    assert "SOUMISSION_PORT=8042" in content
    assert "sqlite:///" in content
    # 2eme appel : pas re-cree
    assert inst.generer_env_si_absent() is False


def test_first_run(tmp_path, monkeypatch):
    import installer_pyside6 as inst
    fake_env = tmp_path / ".env"
    fake_db = tmp_path / "soumission_dz.db"
    monkeypatch.setattr(inst, "ENV_FILE", fake_env)
    monkeypatch.setattr(inst, "DB_FILE", fake_db)
    assert inst.first_run() is True
    fake_env.write_text("k=v")
    fake_db.write_bytes(b"sqlite-fake")
    assert inst.first_run() is False


def test_backup_restore_roundtrip(tmp_path, monkeypatch):
    import installer_pyside6 as inst
    fake_env = tmp_path / ".env"
    fake_db = tmp_path / "soumission_dz.db"
    fake_storage = tmp_path / "storage"
    monkeypatch.setattr(inst, "ENV_FILE", fake_env)
    monkeypatch.setattr(inst, "DB_FILE", fake_db)
    monkeypatch.setattr(inst, "STORAGE_DIR", fake_storage)
    monkeypatch.setattr(inst, "PROJECT_ROOT", tmp_path)

    # Cree des donnees a sauvegarder
    fake_env.write_text("SOUMISSION_JWT_SECRET=test")
    fake_db.write_bytes(b"sqlite-content-fake")
    fake_storage.mkdir()
    (fake_storage / "1").mkdir()
    (fake_storage / "1" / "doc.pdf").write_bytes(b"%PDF-fake")

    # Sauvegarde
    backup = tmp_path / "bk.zip"
    inst.backup_to_zip(backup)
    assert backup.exists()

    # Verifie le contenu
    with zipfile.ZipFile(backup) as zf:
        names = zf.namelist()
        assert "soumission_dz.db" in names
        assert ".env" in names
        assert any("doc.pdf" in n for n in names)

    # Modifie tout puis restaure
    fake_db.write_bytes(b"DESTROYED")
    fake_env.write_text("DESTROYED")
    ok, msg = inst.restore_from_zip(backup)
    assert ok is True, msg
    # La DB est restauree
    assert fake_db.read_bytes() == b"sqlite-content-fake"


def test_service_manager_initial_state():
    from installer_pyside6 import ServiceManager
    sm = ServiceManager(port=18099)
    assert sm.is_running() is False
    assert sm.url() == "http://127.0.0.1:18099"


def test_restore_inexistant():
    from installer_pyside6 import restore_from_zip
    ok, msg = restore_from_zip(Path("/tmp/inexistant_xyz123.zip"))
    assert ok is False
    assert "introuvable" in msg.lower()
