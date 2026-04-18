# -*- coding: utf-8 -*-
"""Sécurité : hachage PBKDF2 + JWT HMAC-SHA256 en stdlib (pas de libs externes)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from app.config import get_settings

PBKDF2_ITERATIONS = 200_000
PBKDF2_SALT_BYTES = 16
PBKDF2_ALGO = "sha256"


# ---------------------------------------------------------------------------
# Hachage de mots de passe (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Hache un mot de passe via PBKDF2-HMAC-SHA256. Format: pbkdf2$iter$salt_b64$hash_b64."""
    if not password or len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caracteres.")
    salt = secrets.token_bytes(PBKDF2_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(PBKDF2_ALGO, password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return (
        f"pbkdf2${PBKDF2_ITERATIONS}$"
        f"{base64.b64encode(salt).decode('ascii')}$"
        f"{base64.b64encode(dk).decode('ascii')}"
    )


def verify_password(password: str, stored: str) -> bool:
    """Vérifie un mot de passe contre un hash stocké. Retourne False si format invalide."""
    try:
        scheme, iters_s, salt_b64, hash_b64 = stored.split("$")
        if scheme != "pbkdf2":
            return False
        iters = int(iters_s)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac(PBKDF2_ALGO, password.encode("utf-8"), salt, iters)
        return hmac.compare_digest(dk, expected)
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# JWT HMAC-SHA256 (stdlib uniquement)
# ---------------------------------------------------------------------------


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


class JWTError(Exception):
    """Erreur de décodage ou vérification du JWT."""


def create_access_token(
    user_id: int,
    organisation_id: int,
    role: str,
    organisation_type: str,
    cabinet_id: int | None = None,
    entreprise_id: int | None = None,
    expires_hours: int | None = None,
) -> str:
    """Génère un JWT HS256 signé."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp_delta = timedelta(hours=expires_hours or settings.jwt_expire_hours)
    payload = {
        "sub": str(user_id),
        "uid": user_id,
        "org_id": organisation_id,
        "org_type": organisation_type,
        "role": role,
        "cabinet_id": cabinet_id,
        "entreprise_id": entreprise_id,
        "iat": int(now.timestamp()),
        "exp": int((now + exp_delta).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    sig = hmac.new(
        settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    sig_b64 = _b64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_access_token(token: str) -> dict:
    """Décode et vérifie un JWT. Lève JWTError si invalide ou expiré."""
    settings = get_settings()
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError as e:
        raise JWTError("token_malformed") from e

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected = hmac.new(
        settings.jwt_secret.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    try:
        provided = _b64url_decode(sig_b64)
    except Exception as e:
        raise JWTError("signature_decode_failed") from e
    if not hmac.compare_digest(expected, provided):
        raise JWTError("bad_signature")

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception as e:
        raise JWTError("payload_decode_failed") from e

    exp = payload.get("exp")
    if exp is None or int(datetime.now(timezone.utc).timestamp()) >= int(exp):
        raise JWTError("token_expired")

    return payload
