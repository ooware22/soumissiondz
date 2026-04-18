---
title: "SOUMISSION.DZ — Cadrage du modèle produit"
subtitle: "3 cas d'usage, plans tarifaires, monétisation, décisions structurantes"
author: "Belhof — Fondateur"
date: "Avril 2026 — Version 5.0 (implémenté)"
---

# Objectif du document

Ce document est le **cadrage fondateur** du modèle produit v5.0. Il a été rédigé en avril 2026 sur la base du terrain (10 prospects interrogés) et a guidé toute la réécriture from scratch.

**État en avril 2026 : tous les éléments cadrés dans ce document sont implémentés dans la v5.0.**

# Les 3 cas d'usage cibles

## Cas 1 — Entreprise autonome

**Profil type :** PME algérienne de 5 à 100 employés qui répond elle-même à ses appels d'offres.

**Exemples prospects identifiés :**

- Brahim (Alpha BTPH, Sidi Bel Abbès, 35 salariés) — BTPH voirie et routes
- Kamel (Batipro, Sétif, 85 salariés) — BTPH gros œuvre et LPP
- Amine (Hydra Études, Alger, 12 salariés) — Bureau d'études hydraulique
- Nadia (Omega Fournitures, Oran, 18 salariés) — Importation matériel
- Omar (Sud Travaux, Ghardaïa, 8 salariés) — Travaux divers Sud

**Besoin :** gagner du temps, éviter les erreurs, fiabiliser la production des dossiers.

**Valeur perçue :** -30 à -50 % de temps de préparation, -90 % d'erreurs fatales (doc expiré, formulaire oublié).

**Organisation technique :**

- 1 `Organisation` type=ENTREPRISE
- 1 `Entreprise` liée
- N `User` (1 à 5 selon plan) avec rôles PATRON / CHEF_DOSSIER / AUDITEUR

**Scoping :** une entreprise voit ses propres données uniquement. Isolation cross-tenant garantie par G2.

## Cas 2 — Cabinet de consultant

**Profil type :** consultant indépendant ou petit cabinet qui prépare les AO pour **plusieurs** entreprises clientes.

**Exemple prospect identifié :**

- Mourad (Cabinet Mourad Conseils, Alger) — 3 à 15 entreprises au portefeuille

**Besoin :** gérer plusieurs clients efficacement, changer de contexte rapidement, éviter les confusions, facturation simplifiée.

**Valeur perçue :** capacité à doubler son volume de clients sans embaucher.

**Organisation technique :**

- 1 `Organisation` type=CABINET
- 1 `Cabinet` lié
- N `Entreprise` avec `cabinet_id = X` (portefeuille)
- 1 ou 2 `User` role=CONSULTANT

**Fonctionnalité clé :** **comparateur inter-entreprises** pour un même AO (quelle entreprise du portefeuille a la meilleure éligibilité ?).

**Plan cible :** EXPERT (20 000 DA/mois) qui inclut le portefeuille illimité.

## Cas 3 — Service d'assistance plateforme

**Profil type :** l'entreprise cliente (Cas 1 ou Cas 2) manque de temps ou d'expertise sur un AO particulier, et délègue temporairement à un **assistant agréé** de la plateforme.

**Exemples d'assistants :**

- Yacine Merabet — spécialités BTPH, VRD, hydraulique
- Samira Bouguerra — spécialités fournitures, services, études

**Besoin côté client :** externaliser ponctuellement la charge d'un AO complexe ou urgent.

**Besoin côté assistant :** avoir un flux régulier de missions rémunérées avec un cadre juridique clair (mandat signé).

**Organisation technique :**

- Assistants regroupés dans `Organisation` type=ENTREPRISE "SOUMISSION.DZ — Assistants"
- `User` role=ASSISTANT_AGREE lié à `AssistantAgree` (spécialités, IBAN, charte signée, note moyenne, historique missions)
- `Mandat` signé électroniquement par le client, donnant un **périmètre borné** d'actions sur l'entreprise
- `Mission` = unité de travail (prestation × entreprise × assistant) avec statut et livrables
- `MissionMessage` pour la messagerie client ↔ assistant
- `AoMandatAction` pour le journal traçable de chaque action dans le périmètre du mandat

**Monétisation :** prestation à l'acte (catalogue 7 prestations), commission plateforme 30 % implicite dans le prix HT.

**Garantie G4 :** traçabilité totale des actions de l'assistant dans le journal `AoMandatAction`.

# Modèle économique

## 6 plans tarifaires

| Code         | Tarif mensuel (DA) | Tarif annuel (DA) | Cible                                  | Inclus                                              |
| ------------ | ------------------ | ----------------- | -------------------------------------- | --------------------------------------------------- |
| `DECOUVERTE` | 0                  | 0                 | Essai gratuit 14 jours                 | Fonctionnalités de base, 1 utilisateur              |
| `ARTISAN`    | 5 000              | 54 000            | TPE solo                               | Cas 1, 1 utilisateur                                |
| `PRO`        | 10 000             | 108 000           | PME 5-30 employés                      | Cas 1, 3 utilisateurs, assistance Cas 3 disponible  |
| `BUSINESS`   | 15 000             | 162 000           | PME 30+, multi-utilisateurs            | Cas 1, utilisateurs illimités, priorité support     |
| `EXPERT`     | 20 000             | 216 000           | Consultants Cas 2 avec portefeuille    | Cas 2, entreprises illimitées, comparateur          |
| `HOTLINE`    | 4 000              | 43 200            | Add-on support sur n'importe quel plan | Tickets illimités, réponse < 24 h                   |

**Remise annuelle : -10 %** (périodicité annuelle économise 2 mois sur 12).

## Modes complémentaires

### À l'acte (sans abonnement)

Pour les entreprises qui ne veulent pas s'engager :

- **5 000 DA / dossier** complet (1 AO de la préparation au dépôt)
- Paiement Edahabia au lancement du dossier
- Pas d'accès à l'historique après clôture

Cible : entreprises avec très peu d'AO par an (< 5).

### Assistance Cas 3

Catalogue de 7 prestations :

| Code                  | Libellé                                    | Prix HT (DA) | Délai max |
| --------------------- | ------------------------------------------ | ------------ | --------- |
| `DOSSIER_CLE_EN_MAIN` | Dossier complet préparé par assistant      | 65 000       | 15 j      |
| `CHIFFRAGE_DQE`       | Construction du DQE avec benchmark prix    | 15 000       | 7 j       |
| `REDACTION_MEMOIRE`   | Rédaction du mémoire technique             | 25 000       | 10 j      |
| `AUDIT_APPROFONDI`    | Audit par expert des 25 règles + rapport   | 12 000       | 5 j       |
| `URGENCE_72H`         | Dossier complet en 72 h max (surtarif)     | 95 000       | 3 j       |
| `FORMATION_1H`        | Formation visio à l'utilisation            | 8 000        | 7 j       |
| `SUIVI_POST_DEPOT`    | Suivi attribution + rédaction recours      | 18 000       | 30 j      |

Prix TTC = prix HT × 1,19 (TVA 19 %).

### Parrainage

20 % de commission sur les paiements du filleul pendant 12 mois.

# Principes de conception non-négociables

## Technique

- **Hébergement en Algérie** (loi 18-07) — Icosnet, Algérie Télécom ou Djaweb pour la version cloud
- **Pas d'IA/LLM** en v5.0 (reporté v6 après retour pilote)
- **Pas d'arabe** dans l'interface (0 prospect sur 10 l'a demandé, français suffisant)
- **Zéro Docker** pour simplifier l'installation chez le pilote
- **Sécurité par construction** : G1 (auth JWT), G2 (isolation cross-tenant), G3 (pas de fuite), G4 (traçabilité Cas 3)

## Commercial

- Pas de free-mium illimité — 14 jours de découverte, puis plan payant obligatoire
- Prix en DA uniquement (pas d'euros ou dollars en v5)
- Factures conformes fiscalité algérienne (NIF, NIS, RC, TVA 19 %)
- Paiement par Edahabia (cible v6) ou virement bancaire (v5)

## Produit

- Pas de feature qui ne vient pas d'un besoin prospect exprimé
- Simplicité > exhaustivité : un utilisateur doit pouvoir faire son 1er AO en < 2 h
- Pas de mobile natif en v5 — SPA responsive suffit
- Pas d'API publique en v5 — à ouvrir en v6 si demande

# Les 40 décisions structurantes (D1 à D40)

Toutes documentées dans `CHANGELOG_v5.md`. Les plus importantes :

| # | Décision                                                        | Justification                            |
| - | --------------------------------------------------------------- | ---------------------------------------- |
| D1 | Python 3.11 min (pas 3.12)                                     | Compatibilité pilotes, StrEnum suffit    |
| D2 | FastAPI + SQLAlchemy 2 + Pydantic 2                            | Stack moderne, types, perf, docs auto    |
| D3 | Pas d'IA en v5                                                 | Risque souveraineté non résolu           |
| D5 | Pas d'arabe UI                                                 | 0 demande prospect, coût élevé           |
| D7 | Zéro Docker                                                    | Pilote local = setup.bat/.exe            |
| D11| SQLite par défaut                                              | Zéro conf, suffit < 50 entreprises       |
| D14| Edahabia mock en v5                                            | Contrat Satim = mois de délai            |
| D18| SPA vanilla JS (pas de React)                                  | Pas de build, ROI négatif v5             |
| D23| 3 tenants distincts vs multi-tenant                            | Simplicité opérationnelle, clarté        |
| D28| Loi 18-07 implémentée complète                                 | Non négociable légalement                |
| D31| Installateur PySide6 + PyInstaller                             | 50 Mo vs 200 Mo Electron                 |
| D35| Factures PDF via reportlab                                     | Léger, contrôle total mise en page       |
| D40| Seeds démo réalistes 2 mois                                    | Démo commerciale crédible                |

# Conformité réglementaire

## Loi 18-07 (protection données personnelles)

Implémentée dans le router `conformite.py` (voir document 04) :

- Page `/confidentialite` avec texte juridique
- Consentement horodaté au signup
- Export ZIP portable
- Soft-delete + purge physique J+30

## Fiscalité algérienne

- Mentions obligatoires sur factures : NIF, NIS, RC, TVA 19 %, RIB plateforme
- Numéro de facture séquentiel par année
- Conservation des factures 10 ans (stockage `storage/factures_archives/`)

## Droit du travail (pour assistants Cas 3)

- Les assistants sont considérés **consultants indépendants**, pas salariés
- Contrat d'agrément + charte signés (PDF dans `storage/assistants/`)
- Facturation plateforme → client, commission plateforme 30 %, virement 70 % à l'assistant

# Ce que la v5 n'est pas

- **Pas** un outil de soumission électronique aux administrations (le dépôt reste physique)
- **Pas** un ERP ni une comptabilité
- **Pas** une bourse de sous-traitance
- **Pas** une place de marché ouverte (les assistants sont recrutés par la plateforme)
- **Pas** un outil de formation académique (capsules possibles en v6 add-on)

# Axes d'évolution envisagés v6+

Voir document 06 — Roadmap. Principaux :

- Paiement Edahabia réel
- IA pour suggestions (non bloquante)
- Hébergement cloud Algérie
- API publique
- Marketplace d'assistants

---

**Ce document fige le modèle produit v5.0. Toute évolution structurelle fera l'objet d'une mise à jour ou d'un document v6 dédié.**
