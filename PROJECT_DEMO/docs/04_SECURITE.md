---
title: "SOUMISSION.DZ — Sécurité"
subtitle: "Garanties G1..G4, isolation cross-tenant, conformité loi 18-07"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Les 4 garanties de sécurité

SOUMISSION.DZ s'engage sur 4 garanties numérotées, chacune couverte par au moins un test automatisé.

## G1 — Authentification valide et horodatée

- Tokens JWT HS256 avec durée de vie configurable (24 h par défaut)
- Secret JWT généré au bootstrap avec `secrets.token_hex(32)` (256 bits cryptographique)
- Mots de passe hashés via **PBKDF2-SHA256 200 000 itérations** (stdlib uniquement, pas de dépendance externe)
- Tokens expirés ou falsifiés → 401
- **Tests** : `test_auth.py` (8 tests) couvre expiration, signature invalide, payload malformé

## G2 — Isolation cross-tenant stricte

- Toute requête métier passe par `Depends(get_current_context)` qui extrait `user_id`, `org_id`, `role` du JWT
- Le scoping (`app/scoping.py`) résout l'`entreprise_id` autorisée selon le profil (Cas 1 / Cas 2 / Cas 3 / Admin)
- Tentative d'accès à une entité d'une autre organisation → **404** (jamais 403, pour ne pas révéler l'existence)
- Les payloads de création/modification **écrasent systématiquement** `organisation_id` et `cabinet_id` avec ceux du contexte (un client malveillant ne peut pas les manipuler)
- **Tests** : `test_isolation.py` (5 tests cross-tenant) + tests dans chaque module (13+ tests d'isolation au total)

## G3 — Pas de fuite d'information par les erreurs

- Messages d'erreur génériques sur les endpoints sensibles (login : « identifiants invalides » sans préciser si l'email existe)
- Logs structurés JSON côté serveur avec tous les détails pour debugging
- Codes HTTP précis mais sans contenu révélateur : 404 plutôt que 403, « not found » plutôt que « forbidden »
- **Tests** : couverts dans les tests d'isolation

## G4 — Traçabilité des actions des assistants Cas 3

- Chaque action d'un assistant dans le cadre d'un mandat est enregistrée dans `AoMandatAction`
- Champs tracés : `mandat_id`, `user_id_assistant`, `action_type`, `action_payload` (JSON), `created_at`
- Actions hors périmètre du mandat → 403 + log du tentative
- Le client entreprise peut consulter le journal complet des actions de son assistant sur son dossier
- **Tests** : `test_phase4.py` (14 tests Cas 3) dont vérification du log

# Mécanismes en détail

## Authentification

```python
# app/security.py — extrait
def hash_password(pw: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt, 200_000)
    return f"pbkdf2_sha256$200000${base64(salt)}${base64(dk)}"

def verify_password(pw: str, stored: str) -> bool:
    # constant-time comparison
    ...

def create_jwt(user_id: int, org_id: int, role: str) -> str:
    payload = {"sub": user_id, "org": org_id, "role": role,
               "iat": now(), "exp": now() + 24h}
    return jwt_encode(payload, SECRET, alg="HS256")
```

Pas de librairie externe pour JWT (évite `python-jose` et ses dépendances, utilise stdlib).

## Contexte d'exécution

```python
# app/deps.py
def get_current_context(
    authorization: Annotated[str, Header()],
    db: Session = Depends(get_db),
) -> Context:
    token = authorization.removeprefix("Bearer ").strip()
    payload = jwt_decode(token, SECRET)
    # Vérification expiration, signature, user existe
    return Context(user_id=..., org_id=..., role=..., user=...)
```

**Tout endpoint métier l'utilise** (sauf `/auth/login`, `/signup/*`, `/health`, `/confidentialite`).

## Scoping par profil

```python
# app/scoping.py
def resolve_entreprise_courante(ctx: Context, db: Session,
                                 x_entreprise_active: int | None = None) -> Entreprise:
    if ctx.role == "PATRON" or ctx.role == "CHEF_DOSSIER":
        # Cas 1 : unique entreprise de l'org
        return db.query(Entreprise).filter(
            Entreprise.organisation_id == ctx.org_id
        ).one()

    if ctx.role == "CONSULTANT":
        # Cas 2 : header obligatoire, vérification cabinet
        if x_entreprise_active is None:
            raise HTTPException(400, "Header X-Entreprise-Active-Id requis")
        ent = db.query(Entreprise).filter(
            Entreprise.id == x_entreprise_active,
            Entreprise.cabinet_id == ctx.cabinet.id,  # vérif portefeuille
        ).one_or_none()
        if ent is None:
            raise HTTPException(404)  # G2 : pas 403
        return ent

    if ctx.role == "ASSISTANT_AGREE":
        # Cas 3 : résolution par mandat actif
        mandat = db.query(Mandat).filter(
            Mandat.assistant_id == ctx.user.assistant.id,
            Mandat.statut == "signe",
            Mandat.valide_jusqu_au >= today(),
        ).one_or_none()
        if mandat is None:
            raise HTTPException(403, "Aucun mandat actif")
        return mandat.entreprise

    raise HTTPException(403)
```

## Nettoyage systématique des payloads

Les payloads Pydantic contiennent **uniquement** les champs métier. Les champs de scoping (`organisation_id`, `cabinet_id`, `entreprise_id`) sont **systématiquement écrasés** par le serveur :

```python
@router.post("/references")
def create_ref(
    payload: ReferenceCreate,
    ctx = Depends(get_current_context),
    db = Depends(get_db),
):
    ent = resolve_entreprise_courante(ctx, db)
    ref = Reference(
        **payload.model_dump(),       # Champs métier uniquement
        entreprise_id=ent.id,         # Écrasé par serveur
    )
    db.add(ref); db.commit()
    return ref
```

**Un patron qui modifie son navigateur pour poster `entreprise_id=99` sur un autre compte obtient un 404.**

# Protection contre les vulnérabilités classiques

## SQL injection

- **ORM SQLAlchemy exclusivement** — pas de `text()` avec interpolation, jamais de f-string dans des requêtes
- Toutes les clauses `where` passent par les expressions SQLAlchemy typées
- **Audit** : `ruff` + revue manuelle avant chaque release

## XSS (front)

- SPA vanilla JS — le seul endroit où on injecte du HTML est via `element.innerHTML = ...` pour les tableaux de données
- Toutes les valeurs dynamiques sont escapées via `element.textContent = ...` ou des templates bornés
- Pas d'eval, pas de new Function

## CSRF

- Le front utilise un token JWT dans le header `Authorization`, pas un cookie → **pas de vulnérabilité CSRF classique**
- Pour l'usage par cookie (envisagé en v6), prévoir CSRF token double-submit

## Path traversal (uploads)

- Les fichiers uploadés sont stockés avec un nom généré serveur : `{document_id}_{safe_filename}`
- `safe_filename` filtre `..`, `/`, `\` avec regex stricte
- Storage dans `storage/{entreprise_id}/documents/` avec vérification que `entreprise_id` correspond au contexte
- Endpoint de téléchargement vérifie systématiquement le scoping avant de servir le fichier

## Rate limiting

- **Pas encore implémenté** (reporté v6). À prévoir pour : `/auth/login` (bruteforce), `/signup/*` (création de comptes massifs), `/coffre/documents` (DoS par upload).
- Mitigation partielle actuelle : logs structurés permettent détection manuelle.

## Brute force mot de passe

- **Pas de compte verrouillé** en v5.0 (reporté v6 car les 4 pilotes ont peu d'utilisateurs).
- PBKDF2-SHA256 200 000 itérations ralentit mécaniquement les attaques hors-ligne.

# Conformité loi 18-07 (protection données personnelles DZ)

Implémenté dans le router `conformite.py` :

## Page `/confidentialite`

Texte juridique expliquant :

- Nature des données collectées (coordonnées, documents administratifs, historique marchés)
- Finalités (gestion des dossiers de soumission, facturation, assistance)
- Durée de conservation (active tant que le compte existe, puis 5 ans après résiliation)
- Droits : accès, rectification, opposition, portabilité, effacement
- Procédure pour exercer ces droits (email `support@soumission.dz`)

## Consentement horodaté

- Checkbox obligatoire au signup
- Enregistrement `consent_at: datetime` dans la table `User`
- Pas de consentement = pas de création de compte

## Export des données (portabilité)

- Endpoint `GET /confidentialite/export` accessible à tout utilisateur authentifié
- Retourne un **ZIP** contenant :
  - `data.json` (toutes les données métier de l'entreprise)
  - `documents/` (tous les PDFs uploadés)
  - `README.txt` explicatif
- Format ouvert, réutilisable par le concurrent si besoin

## Soft-delete J+30 (droit à l'oubli)

- `DELETE /confidentialite/compte` marque `deleted_at = now()` sur l'Organisation
- Accès immédiatement coupé
- Purge physique définitive après **30 jours** (permet annulation pendant ce délai)
- Job de purge : à lancer quotidiennement (cron ou scheduler applicatif). Voir `app/tasks/purge.py`.

## Logs des accès aux données personnelles

Loguru structuré, rotation et archivage prévus pour audit de conformité en cas de contrôle ARPCE.

# Tests de sécurité (13+ tests)

```
tests/test_isolation.py               : 5 tests cross-tenant G2
tests/test_auth.py                    : 8 tests G1 (expiration, signature)
tests/test_phase2.py::test_*_isolation: dans chaque module
tests/test_phase3.py::test_*_isolation: cabinet, dossier, caution
tests/test_phase4.py::test_mandat_*   : G4 journal actions
```

Exemple type :

```python
def test_patron_A_ne_voit_pas_references_patron_B(client, db):
    # A signup + crée ref
    ca = signup_entreprise(client, "A")
    rid = create_ref(client, ca.token, "Travaux A")
    # B signup
    cb = signup_entreprise(client, "B")
    # B tente de lire la ref de A
    resp = client.get(f"/references/{rid}",
                      headers={"Authorization": f"Bearer {cb.token}"})
    assert resp.status_code == 404   # G2 : 404 et pas 403
```

# Audit et certification envisagés

- **Pas de certification ISO 27001** en v5.0 (coût disproportionné vs volume)
- **Audit de sécurité externe** envisagé post-pilotes, avant passage production hébergée
- **Déclaration ARPCE** (Autorité Régulation DZ) dès le passage en hébergement cloud Algérie

# Check-list sécurité pre-déploiement

- [ ] JWT_SECRET généré aléatoirement et non commité dans git
- [ ] HTTPS obligatoire en production (Let's Encrypt via certbot)
- [ ] `SOUMISSION_ENV=production` dans `.env` prod (désactive docs et tracebacks détaillés)
- [ ] Logs anonymisés pour export (pas d'emails, pas de NIF en clair dans logs partagés)
- [ ] Backup quotidien chiffré de la base
- [ ] Politique de rotation des secrets documentée
- [ ] Plan de réponse incident rédigé (qui prévenir, qui coupe quoi)
