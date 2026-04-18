# -*- coding: utf-8 -*-
"""Extracteur de champs AO depuis un PDF — regex + heuristiques, pas d'IA."""
from __future__ import annotations

import io
import re
from dataclasses import dataclass
from datetime import date, datetime

from pypdf import PdfReader


@dataclass
class AoExtraction:
    reference: str | None = None
    objet: str | None = None
    maitre_ouvrage: str | None = None
    wilaya_code: str | None = None
    date_limite: date | None = None
    budget_estime_da: int | None = None
    qualification_requise_cat: str | None = None
    texte_brut: str = ""


# Regex cles — heuristiques conservatrices (mieux vaut None que faux positif).
_RE_REF = re.compile(r"(?:reference|ref|appel\s*d'?offres?\s*n[\u00b0\s]*[oO:])\s*[:=\-]?\s*([A-Z0-9][\w\-/\.]{3,40})", re.IGNORECASE)
_RE_OBJET = re.compile(r"objet\s*[:\-]\s*([^\n]{10,400})", re.IGNORECASE)
_RE_MO = re.compile(r"(?:maitre\s+d'?ouvrage|administration)\s*[:\-]\s*([^\n]{3,200})", re.IGNORECASE)
_RE_BUDGET = re.compile(r"(?:budget|montant\s+estim[eé]|enveloppe)[^\d]{0,30}([\d\s.,]{4,20})\s*(?:DA|dinar)", re.IGNORECASE)
_RE_DATE = re.compile(r"(?:date\s+limite|date\s+de\s+d[eé]p[oô]t|avant\s+le)[^\d]{0,20}(\d{1,2})[\/\-\.\s](\d{1,2}|\w{3,10})[\/\-\.\s](\d{2,4})", re.IGNORECASE)
_RE_WILAYA = re.compile(r"wilaya(?:\s+(?:de|d'))?\s+([A-Z][A-Za-z\u00c0-\u024f\s\-]{2,30})", re.IGNORECASE)
_RE_QUAL = re.compile(r"qualification\s+(?:cat[eé]gorie\s+)?([IVX]{1,4})", re.IGNORECASE)

# Wilayas algeriennes — 48 codes (1-58 avec trous)
WILAYAS = {
    "adrar": "01", "chlef": "02", "laghouat": "03", "oum el bouaghi": "04",
    "batna": "05", "bejaia": "06", "biskra": "07", "bechar": "08",
    "blida": "09", "bouira": "10", "tamanrasset": "11", "tebessa": "12",
    "tlemcen": "13", "tiaret": "14", "tizi ouzou": "15", "alger": "16",
    "djelfa": "17", "jijel": "18", "setif": "19", "saida": "20",
    "skikda": "21", "sidi bel abbes": "22", "annaba": "23", "guelma": "24",
    "constantine": "25", "medea": "26", "mostaganem": "27", "msila": "28",
    "mascara": "29", "ouargla": "30", "oran": "31", "el bayadh": "32",
    "illizi": "33", "bordj bou arreridj": "34", "boumerdes": "35",
    "el tarf": "36", "tindouf": "37", "tissemsilt": "38", "el oued": "39",
    "khenchela": "40", "souk ahras": "41", "tipaza": "42", "mila": "43",
    "ain defla": "44", "naama": "45", "ain temouchent": "46", "ghardaia": "47",
    "relizane": "48",
}

_MONTHS_FR = {
    "janvier": 1, "fevrier": 2, "février": 2, "mars": 3, "avril": 4, "mai": 5,
    "juin": 6, "juillet": 7, "aout": 8, "août": 8, "septembre": 9,
    "octobre": 10, "novembre": 11, "decembre": 12, "décembre": 12,
}


def _parse_date(d: str, m: str, y: str) -> date | None:
    try:
        day = int(d)
        if m.isdigit():
            month = int(m)
        else:
            month = _MONTHS_FR.get(m.lower().strip(), 0)
            if not month:
                return None
        year = int(y)
        if year < 100:
            year += 2000
        return date(year, month, day)
    except (ValueError, TypeError):
        return None


def _parse_montant(s: str) -> int | None:
    # Nettoie: enleve espaces, points separateurs. Virgule = decimale FR.
    s = s.replace(" ", "").replace("\u00a0", "")
    if "," in s:
        s = s.split(",")[0]
    s = s.replace(".", "")
    try:
        return int(s) if s.isdigit() else None
    except ValueError:
        return None


def _detect_wilaya(text: str) -> tuple[str | None, str | None]:
    lower = text.lower()
    for nom, code in WILAYAS.items():
        if nom in lower:
            return code, nom.title()
    return None, None


def extract_from_pdf_bytes(data: bytes) -> AoExtraction:
    """Extraction principale — lit le PDF, applique les regex, renvoie AoExtraction."""
    result = AoExtraction()
    try:
        reader = PdfReader(io.BytesIO(data))
        pages_text = []
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception:
                pages_text.append("")
        text = "\n".join(pages_text)
    except Exception:
        return result

    result.texte_brut = text[:5000]

    if m := _RE_REF.search(text):
        result.reference = m.group(1).strip().rstrip(".,;:")
    if m := _RE_OBJET.search(text):
        result.objet = m.group(1).strip().rstrip(".,;")
    if m := _RE_MO.search(text):
        result.maitre_ouvrage = m.group(1).strip().rstrip(".,;")
    if m := _RE_BUDGET.search(text):
        result.budget_estime_da = _parse_montant(m.group(1))
    if m := _RE_DATE.search(text):
        result.date_limite = _parse_date(m.group(1), m.group(2), m.group(3))
    if m := _RE_QUAL.search(text):
        result.qualification_requise_cat = m.group(1).upper()

    code, _nom = _detect_wilaya(text)
    if code:
        result.wilaya_code = code

    return result
