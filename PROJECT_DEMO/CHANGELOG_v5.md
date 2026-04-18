# CHANGELOG v5.0 — SOUMISSION.DZ

## [5.0.0-final] — 2026-04-13 — v5.0 complete (Lots 1 a 9)

**Etat global : 105 tests pytest verts, 4 migrations Alembic, 9 lots livres.**

```
tests/test_signup.py    : 6   tests
tests/test_auth.py      : 8   tests   (G1 token expire)
tests/test_isolation.py : 5   tests   (G2/G3 cross-tenant)
tests/test_team.py      : 4   tests
tests/test_phase2.py    : 26  tests   (Lots 2+3)
tests/test_phase3.py    : 18  tests   (Lots 4+5)
tests/test_phase4.py    : 14  tests   (Lot 6 — Cas 3)
tests/test_phase5.py    : 20  tests   (Lots 7+8)
tests/test_installer.py : 4   tests   (Lot 9)
                         ===
                         105 verts
```

---

## Lot 1 — Fondation

- Modeles `Organisation`, `Entreprise`, `Cabinet`, `User` + 4 enums
  (OrgType, OrgStatut, PlanCode, UserRole)
- Securite : JWT HS256 stdlib, PBKDF2-SHA256 200k iterations
- `app/deps.py` get_current_context (resout user+org+role+entreprise+cabinet)
- Endpoints `/signup/entreprise`, `/signup/cabinet`, `/auth/login`,
  `/auth/me`, `/team`, `/team/invite`, `/health`
- Header `X-Entreprise-Active-Id` pour Cas 2
- Migration Alembic 0001_initial

## Lot 2 — Coffre-fort + References

- Modele `Document` (15 types officiels algeriens), `Reference`
- Router `/coffre` : types, upload PDF, list, download, PATCH metadata,
  delete, alertes 7j/15j/30j/expire
- Router `/references` : CRUD complet
- Stockage `storage/{entreprise_id}/documents/{doc_id}_{filename}`

## Lot 3 — AO + Audit + Simulateur + Templates + Memoire + Formulaires

- Modeles `AppelOffres`, `PrixArticle`
- `/ao` CRUD + `/import-pdf` (regex pure, 48 wilayas detectees)
- `rules_engine.py` : 25 regles ponderees (documents x10, bilans x3,
  qualification x2, planning, finance, references x3, identite x3, geo)
- `/prix` : catalogue 35 articles BTPH (8 categories) + simulateur
  bas/ok/haut/hors_fourchette
- `/templates` : 5 templates (ROUTES, BATIMENT_PUBLIC, VRD, LPP,
  HYDRAULIQUE) avec chiffrage proportionnel
- `/memoire/generer` : DOCX 7 sections via python-docx
- `/formulaires/{code}/generer` : 3 DOCX (declaration_probite,
  lettre_soumission, declaration_a_souscrire)
- Migration Alembic 0002_lots23
- `app/scoping.py` : helper resolve_entreprise_courante (Cas 1 + Cas 2)

## Lot 4 — Kanban + Workflow + Cautions + Historique

- Modele `Dossier` (7 etapes, 4 statuts Kanban)
- `/dossiers` : CRUD + avancer + valider (workflow 3 niveaux) + kanban
- Modele + `/cautions` (3 types : soumission, bonne_execution, retenue) +
  alertes + lettre recuperation
- Modele + `/soumissions` historique (rang, montant, ecart_pct, statut)

## Lot 5 — Cabinet (Cas 2 complet)

- `/cabinet/entreprises` POST/GET (portefeuille N entreprises)
- `/cabinet/comparer?ao_id=X` audit cross-portefeuille avec ranking par score

## Lot 6 — Cas 3 Assistance

- 6 nouveaux modeles : AssistantAgree, PrestationCatalogue, Mandat,
  Mission, AoMandatAction, MissionMessage
- 7 prestations seeds : MAJ_COFFRE 8000DA, DOSSIER_CLE_EN_MAIN 35000,
  CHIFFRAGE_DQE 15000, REDACTION_MEMOIRE 12000, URGENCE_72H 65000,
  ACCOMPAGNEMENT_DEPOT 10000, FORFAIT_MENSUEL 25000
- `/assistance/prestations` (catalogue)
- `/missions` POST demander / GET list+detail
- `/missions/{id}/signer-mandat` (acceptation horodatee + IP + UA)
- `/missions/{id}/livrer` (reserve assistant + mandat valide + log)
- `/missions/{id}/valider` / `/contester` (note + commentaire 48h)
- `/missions/{id}/journal` (audit trail mandat)
- `/missions/{id}/messages` (messagerie dediee mission)
- `/admin/assistants` recrutement par admin_plateforme

## Lot 7 — Monetisation

- 6 modeles : Plan, Abonnement, Facture, CodeParrainage, Commission,
  TicketHotline
- `/plans` (6 plans seeds DECOUVERTE/ARTISAN/PRO/BUSINESS/EXPERT/HOTLINE)
- `/abonnements` (souscrire mensuel/annuel + facture proforma auto)
- `/factures` (lister + payer + PDF reportlab conforme NIF/NIS/RC + TVA 19%)
- 3 modes paiement : virement (manuel admin), edahabia/cib (mock),
  a_l_acte
- `/parrainage/mon-code` (genere code unique idempotent)
- `/parrainage/mes-commissions` (listing)
- `/hotline` (tickets 3 niveaux) + `/hotline/{id}/repondre` (admin)

## Lot 8 — Conformite loi 18-07

- `/confidentialite` page publique (texte CGU + droits)
- `/confidentialite/cgu` consentement horodate logge
- `/confidentialite/export` ZIP JSON+README de toutes les donnees
  (password_hash REDACTED)
- `/confidentialite/compte` (DELETE) soft-delete (statut suspendu +
  users.actif=False)
- `purger_comptes_expirees(db)` job purge J+30 (a brancher cron)
- Logging structure JSON loguru avec mention article loi 18-07

## Lot 9 — Installateur PySide6

- `installer/installer_pyside6.py` (~330 LOC)
- QMainWindow + boutons Demarrer/Arreter/Redemarrer/Ouvrir nav/Verifier
- ServiceManager : docker compose db + alembic upgrade + uvicorn en bg
- Generation .env automatique avec secrets.token_hex(32) pour JWT_SECRET
- Verification prerequis (Python 3.12, Docker, deps)
- Console de logs en temps reel
- 4 tests unitaires sur les helpers purs (test_installer.py)
- Empaquetage Windows : commentaire pyinstaller en tete du module

---

# Decisions documentees

## D1..D10 — Phase 1 (Lot 1 fondation)
1. Plan defaut Cas 1 = DECOUVERTE
2. Plan defaut Cas 2 = EXPERT
3. Statut defaut = actif
4. Email unique cross-tenant
5. Cabinet sans entreprise au signup
6. Entreprise.organisation_id nullable (Cas 2 n'a pas d'org dediee)
7. PBKDF2 stdlib (pas bcrypt)
8. Roles invitables : validateur/preparateur/lecteur (pas patron)
9. 404 sur entreprise_active_id invalide (G2)
10. Tests SQLite, prod PostgreSQL — modeles 100% portables

## D11..D20 — Phase 2 (Lots 2+3)
11. Extraction PDF = regex pure, pas d'IA
12. 25 regles d'audit ponderees (cf. rules_engine.py)
13. Seed prix auto a la demande
14. Templates en dur (catalogue_seed.py), pas de table DB
15. DOCX uniquement pour livrables texte
16. Alertes expiration fenetre 30j max
17. X-Entreprise-Active-Id obligatoire pour cabinet sur endpoints metier
18. Resolution entreprise centralisee (app/scoping.py)
19. Stockage local storage/ (S3 reporte cloud Algerie)
20. Download avec nom original (prefixe doc_id_ en interne)

## D21..D30 — Phase 3 (Lots 4+5) — voir tests/test_phase3.py
21. 7 etapes Kanban figees
22. Workflow validation : preparateur -> validateur -> patron
23. Caution : 3 types fixes, calcul auto montant si ratio AO fourni
24. Historique soumissions : ecart_pct stocke en x100 entier (evite float)
25. Cabinet ajoute entreprise : cabinet_id force = ctx
26. Comparateur cross-portefeuille reutilise rules_engine.run_audit
27. Vue portefeuille avec indicateurs (dossiers/alertes/soumissions mois)
28. Pas de role consultant_assistant dans le cabinet (consultant seul)
29. Suppression entreprise du portefeuille en CASCADE (toutes donnees)
30. Lettre recuperation caution = template DOCX simple

## D31..D40 — Phase 5 (Lots 7+8+9)
31. Plans hardcodes (PLANS_SEED), idempotent, sans migration data
32. Numerotation factures SDZ-{annee}-{N:05d}, reset annuel
33. TVA 19% en dur (pas configurable)
34. PDF facture via reportlab (pas LibreOffice)
35. Edahabia/CIB en mock (vraie integration v5.5)
36. Code parrainage idempotent, format SDZ-{8 hex}
37. Calcul commissions parrainage non automatise (cron a brancher v5.1)
38. Hotline operateur = admin_plateforme (pas de role separe)
39. Soft-delete = statut suspendu + users.actif=False (pas de deleted_at)
40. Installateur PySide6 sans test e2e (pas de DISPLAY en CI), helpers
    purs testes uniquement
