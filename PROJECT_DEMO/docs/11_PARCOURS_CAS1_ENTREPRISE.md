---
title: "SOUMISSION.DZ — Parcours Cas 1 détaillé"
subtitle: "Du premier clic à la soumission déposée, cas de Brahim / Alpha BTPH"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Contexte

Ce document trace le parcours utilisateur détaillé du **Cas 1 — Entreprise autonome**, avec l'exemple de Brahim (Alpha BTPH, Sidi Bel Abbès, SARL 35 salariés, BTPH qualification IV).

C'est le cas le plus fréquent (~80 % des pilotes et clients cibles en v5). Les 2 autres cas (cabinet et assistance) sont des compléments ou des variantes.

# Jour J-7 — Découverte

## Mercredi, 14 h

Brahim reçoit un `.exe` par WeTransfer envoyé par Belhof après leur RDV de démo en présentiel. Email contient :

- Lien de téléchargement (~50 Mo)
- Mot de passe du ZIP
- PDF d'instructions 4 pages (couleur)
- Numéro de téléphone de Belhof pour assistance immédiate

## Mercredi, 14 h 20

Brahim télécharge et décompresse sur son poste Windows 11.

Double-clique sur `soumission-dz.exe` → Windows SmartScreen affiche un avertissement (pas encore signé code) → clic "Exécuter quand même" (Belhof a prévenu).

## Mercredi, 14 h 25

Wizard d'installation s'ouvre. 5 pages :

1. Bienvenue → Suivant
2. Vérification prérequis : Python 3.11.7 détecté, 7 dépendances manquantes → clic "Installer les dépendances manquantes" → pip tourne 2 min → tout passe vert → Suivant
3. Configuration : dossier par défaut accepté (`C:\Users\Brahim\SOUMISSION.DZ\`), port 8000 libre, case "Lancer au démarrage" cochée, case "Charger les données de démonstration" **décochée** (il veut commencer propre) → Suivant
4. Installation : barre de progression, logs défilent (création `.env`, `alembic upgrade head`, OK, OK, OK) → 15 secondes → Terminé → Suivant
5. Terminé : clic "Lancer SOUMISSION.DZ maintenant"

## Mercredi, 14 h 28

Le navigateur s'ouvre sur `http://127.0.0.1:8000`. Écran de login.

# Jour J-6 à J-1 — Onboarding

## Signup

Brahim clique "Inscription entreprise". Formulaire long mais guidé :

- Email `brahim@alpha-btph.dz` (son mail pro)
- Mot de passe `BrahmM@ns2026!` (8 caractères + mixte, accepté)
- Confirmation
- Nom entreprise `Alpha BTPH`
- Forme juridique `SARL`
- NIF `099922001234567`, NIS `09992200123`
- RC `22/00-1234567 B 18`
- Gérant `Brahim Mansouri`
- Wilaya `22 — Sidi Bel Abbès`
- Adresse, téléphone
- Secteur `BTPH`, activité `Travaux publics voirie et bâtiments`
- Effectif `35`, CA moyen `180 000 000` DA
- Qualification BTPH catégorie `IV`, expiration `30/06/2027`
- Checkbox CGU + loi 18-07

Soumission → redirection dashboard. Token stocké en session.

## Étape 1 — Profil complet (1 h)

Dashboard affiche : "Bienvenue Brahim, voici vos prochaines étapes" avec 5 tâches en checklist.

Il complète les quelques champs optionnels manquants dans le profil (site web, compte bancaire pour cautions, etc.).

## Étape 2 — Coffre-fort (2 h)

Il prépare un dossier avec tous ses PDFs sur le bureau, puis :

- Ouvre l'écran **Coffre**
- Pour chaque type de document, clique "Uploader", sélectionne le PDF, renseigne date d'émission et date d'expiration

Documents chargés ce jour :

| Type                   | Expiration        |
| ---------------------- | ----------------- |
| CNAS                   | 30/06/2026        |
| CASNOS                 | 30/06/2026        |
| CACOBATPH              | 31/12/2026        |
| NIF                    | sans expiration   |
| NIS                    | sans expiration   |
| RC                     | sans expiration   |
| Extrait de rôle        | 31/05/2026        |
| Attestation fiscale    | 30/04/2026        |
| Statuts                | sans expiration   |
| Casier judiciaire      | 15/06/2026        |
| Bilan 2023             | sans expiration   |
| Bilan 2024             | sans expiration   |
| Qualification BTPH IV  | 30/06/2027        |
| Attestation bancaire   | 20/04/2026        |

14 documents uploadés en 1 h 45.

Dashboard : compteurs à jour, **3 alertes d'expiration** (attestation bancaire à 20/04 soit 7 jours, attestation fiscale à 15 j, extrait à 30 j).

Brahim note mentalement d'aller à la banque demain pour renouveler l'attestation. **L'outil vient de lui faire économiser un dépôt manqué.**

## Étape 3 — Références (45 min)

Il saisit 6 références de marchés précédents :

1. Route rurale RC 22-12, APC SBA, 2021, 38 000 000 DA, routes
2. École primaire Chouhada, DEP SBA, 2022, 52 000 000 DA, bâtiment public
3. Voirie zone industrielle extension, DTP SBA, 2023, 68 000 000 DA, VRD
4. Salle polyvalente Merine, APC Merine, 2023, 42 000 000 DA, bâtiment public
5. Réfection piste agricole Sfisef, Direction Agri, 2024, 28 000 000 DA, routes
6. Collecteur eaux pluviales, ADE SBA, 2024, 55 000 000 DA, VRD

CA cumulé sur 4 ans : 283 000 000 DA. Solide.

## Étape 4 — Invitation d'un utilisateur

Il ajoute son chef de dossier Samir (`samir@alpha-btph.dz`, rôle CHEF_DOSSIER). Invitation par email, Samir crée son mot de passe à J+1.

## Étape 5 — Choix du plan

Après 14 jours de DECOUVERTE, il doit choisir. Ouvre l'écran **Facturation** :

- ARTISAN (5 000 DA, 1 utilisateur) : insuffisant (il a Samir)
- PRO (10 000 DA, 3 utilisateurs) : correct pour sa taille
- BUSINESS (15 000 DA, illimité) : surdimensionné pour l'instant

Il choisit **PRO mensuel**, clic "Souscrire mensuel". Facture 11 900 DA TTC générée, paiement mock Edahabia → statut "payée".

**Total onboarding : ~5 h étalées sur 6 jours.**

# Jour J — Premier AO traité

## Contexte

Brahim reçoit par email du Directeur des Travaux Publics de SBA :

- PDF du cahier des charges pour la réfection de la route RN13 sur 5 km
- Budget estimé par le MO : 120 000 000 DA
- Qualification requise : IV + activités routes
- Date limite de dépôt : J+21 à 14 h

## Action 1 — Import PDF (5 min)

- Ouvre écran **AO**
- Clic "Importer PDF"
- Sélectionne le fichier CPT
- Backend lance `pdf_extractor.py` sur le contenu

Résultat affiché après 4 secondes :

| Champ                    | Valeur extraite                              |
| ------------------------ | -------------------------------------------- |
| Référence                | `AO-2026/078` (extrait en-tête)              |
| Objet                    | `Réfection chaussée RN13 sur 5 km`           |
| Maître d'ouvrage         | `Direction des Travaux Publics SBA`          |
| Wilaya                   | `22 — Sidi Bel Abbès`                        |
| Date limite              | `2026-05-04` (21 jours)                      |
| Budget estimé            | `120 000 000 DA`                             |
| Qualification requise    | `IV`                                         |
| Activités requises       | `travaux routes`                             |

Brahim vérifie les champs visuellement, corrige une virgule dans l'objet, enregistre.

## Action 2 — Audit (2 min)

- Clic "Lancer l'audit" sur l'AO fraîchement créé
- Moteur évalue les 25 règles en 1 seconde

Résultat :

```
Score global : 88 / 100
  OK         : 20 règles
  Warning    :  4 règles
  Danger     :  1 règle
```

Détail des warnings / danger :

- ⚠ **Attestation bancaire expire dans 7 jours** (sera périmée au moment du dépôt si pas renouvelée) — catégorie documents
- ⚠ **Casier judiciaire expire dans 63 jours** (OK pour cet AO mais à surveiller) — catégorie documents
- ⚠ **Date limite dans 21 jours** (serré mais faisable) — catégorie calendrier
- ⚠ **Qualification catégorie IV juste suffisante** (pas de marge) — catégorie qualification
- ❌ **Pas de référence en route principale de catégorie IV** (ses références routes sont RC et piste, pas RN) — catégorie cohérence

Brahim prend note :

- Demain : aller à la banque pour attestation renouvelée (action immédiate)
- Pour le mémoire : insister sur l'expérience routes même si pas d'exemple RN strict

## Action 3 — Création du dossier

- Clic "Créer un dossier pour cet AO"
- Nom proposé automatiquement : "Dossier AO-2026/078 — Réfection RN13"
- Statut : À faire
- Date cible (= date dépôt - 2 j) : 2 mai 2026

## Action 4 — Chiffrage (3 h)

Brahim ouvre l'écran **Chiffrage**, onglet **Templates**.

- Sélectionne template `ROUTES`
- Budget cible 115 000 000 DA (il veut être 4 % sous le budget estimé)
- Clic "Chiffrer"

Le template ROUTES propose 6 postes avec quantités proportionnelles :

| Code     | Libellé                          | Unité | Quantité | PU    | Total       |
| -------- | -------------------------------- | ----- | -------- | ----- | ----------- |
| TER001   | Décapage terre végétale          | m³    | 3 200    | 950   | 3 040 000   |
| GRO002   | Couche de base tout-venant       | m³    | 4 800    | 5 200 | 24 960 000  |
| VRD005   | Enrobé bitumineux BB 0/14        | t     | 1 600    | 16 500| 26 400 000  |
| VRD008   | Bordures de trottoir             | ml    | 5 000    | 2 800 | 14 000 000  |
| VRD012   | Signalisation horizontale        | ml    | 10 000   | 850   | 8 500 000   |
| DIV020   | Divers ouvrages d'art            | U     | 15       | 2 500 000 | 37 500 000 |
| **TOTAL**|                                  |       |          |       | **114 400 000** |

Clic "Importer ces postes dans le simulateur".

Passe sur l'onglet **Simulateur**, vérifie ligne à ligne :

- Colonne "Prix moyen marché" auto-remplie
- Ses prix proposés sont très proches des moyennes
- Clic "Simuler"

Résultat : 5 verdicts `ok`, 1 verdict `bas` sur TER001 (950 DA/m³ alors que moyen marché 1 100). Il ajuste à 1 050 → tous verts.

Export CSV du DQE pour discussion interne avec Samir.

## Action 5 — Génération du mémoire DOCX (2 min)

- Clic "Générer mémoire" sur l'AO
- Backend utilise `docx_generator.py` avec les 6 références et les infos entreprise
- DOCX téléchargé : `memoire_AO-2026_078.docx` (120 Ko)

Brahim ouvre dans Word :

- **Section 1** — Présentation de l'entreprise (nom, forme, NIF, NIS, RC, gérant, wilaya, effectif, CA)
- **Section 2** — Qualification et agréments (catégorie IV, CACOBATPH valide)
- **Section 3** — Références pertinentes (6 références, avec montants et années)
- **Section 4** — Méthodologie proposée pour l'AO (texte générique à personnaliser)
- **Section 5** — Moyens humains affectés (à compléter manuellement)
- **Section 6** — Moyens matériels (à compléter)
- **Section 7** — Planning prévisionnel (à compléter)

Il passe 1 h 30 à personnaliser les sections 4-7 avec Samir.

Re-sauvegarde le DOCX final, le ré-uploade dans le dossier pour archive.

## Action 6 — Génération des 3 formulaires (1 min)

- Clic "Générer formulaires" sur le dossier
- 3 fichiers téléchargés :
  - `engagement_honneur_AO-2026_078.docx`
  - `declaration_probite_AO-2026_078.docx`
  - `liste_references_AO-2026_078.docx`

Impression, signature Brahim, tampon humide. Scan des exemplaires pour archive.

## Action 7 — Caution (J+18)

- Récupère à la banque la caution de soumission 1 % de 120 000 000 = 1 200 000 DA
- Banque : BNA, référence `CS-748291`
- Saisie dans SOUMISSION.DZ : `POST /dossiers/{id}/cautions` avec type `caution_soumission`, montant, banque, date émission, référence, statut `active`

## Action 8 — Avancement du dossier

Brahim déplace progressivement le dossier dans le Kanban :

- J+5 : profil validé → étape `documents`
- J+6 : docs complets (attestation renouvelée) → étape `audit`
- J+7 : audit OK → étape `chiffrage`
- J+10 : DQE finalisé → étape `memoire`
- J+13 : mémoire rédigé → étape `verification`
- J+18 : vérification finale + caution obtenue → étape `depot`

## Action 9 — Dépôt (J+19)

Brahim et Samir se rendent au siège de la DTP à 11 h :

- Dossier organisé dans un classeur bleu selon l'ordre du CPT
- Remise au bureau des marchés
- Accusé de réception obtenu (numéro `AR-2026/4521`, reçu à 11 h 42)

De retour au bureau, dans SOUMISSION.DZ :

- Ouvre le dossier
- Clic "Confirmer le dépôt"
- Saisie date `2026-04-28 11:42`, numéro AR `AR-2026/4521`
- Statut dossier → `termine`, création automatique d'une ligne **Soumission** avec `date_depot`

# Jour J+30 — Séance d'ouverture des plis

À 9 h à la DTP, Brahim assiste à la séance.

4 concurrents ont déposé. Il est **2e** derrière ETB Saidi (109 500 000 DA, Brahim était à 114 400 000 DA).

De retour au bureau :

- Ouvre la soumission dans SOUMISSION.DZ
- Met à jour `rang = 2`
- Attend le résultat final (analyse technique + financière peut prendre 60 j)

# Jour J+70 — Résultat définitif

Notification par courrier : **ETB Saidi est attributaire**. Brahim est 2e.

- Met à jour `Soumission.statut = perdu`, `montant_attributaire_da = 109 500 000`, `ecart_pct = 4`, `raison_libre = "Prix plus élevé de 4 % que l'attributaire"`
- Récupère la caution de soumission à la BNA (retour automatique si pas retenu) → met à jour `Caution.statut = recuperee`

Dashboard historique : "18 soumissions déposées cette année, 12 gagnées, 4 perdues, 2 en attente. Taux de gain 67 %."

# Bilan de ce 1er AO

- **Temps total** : ~6 h de travail propre (import + audit + chiffrage + mémoire + formulaires + vérification + dépôt)
- **Avant SOUMISSION.DZ** : ~15 h pour un dossier équivalent
- **Gain** : -60 % de temps
- **Qualité** : 0 oubli critique (l'audit a détecté l'attestation bancaire expirante)

Brahim annonce à Belhof : il signe le passage payant à PRO et accepte d'être cité comme référence.

# Jours suivants — Rythme de croisière

Sur les 12 semaines suivantes, Brahim traite 4 AO :

| AO                              | Statut     | Gain                          |
| ------------------------------- | ---------- | ----------------------------- |
| Route RN13 (premier)            | Perdu      | 2e, écart 4 %                 |
| Construction centre santé rural | **Gagné**  | 78 000 000 DA, attributaire   |
| Piste agricole 8 km             | **Gagné**  | 28 400 000 DA                 |
| Voirie extension zone indus     | En cours   | Résultat attendu J+50         |

Taux de réussite 50 % (2/4 finalisés gagnés). Brahim reste enthousiaste.

Abonnement PRO renouvelé chaque mois. Code de parrainage activé, recommande à 2 confrères (Kamel de Batipro et un sous-traitant de Relizane).

# Frictions remontées (pour backlog v5.x)

- Import PDF : sur 1 des 4 AO, la wilaya n'a pas été détectée (code OCR illisible). Corrigé manuellement. À améliorer la regex.
- Chiffrage : pas de template pour les AO de fournitures pures (Brahim fait parfois de la fourniture de matériel). À ajouter en v5.1.
- Mémoire DOCX : la section "Moyens matériels" est trop générique, il passe 1 h à la réécrire à chaque fois. Demande : permettre de sauvegarder un "profil matériel" réutilisable.
- Kanban : il aimerait pouvoir filtrer par wilaya et par type de travaux. À ajouter en v5.2.
- Alertes d'expiration : il aimerait recevoir un email en plus du dashboard. À ajouter en v5.1 (SMTP simple).

Ces 5 remontées sont classées par priorité :

- P1 : alertes email (tous les pilotes en profiteront) — v5.1
- P1 : template fournitures — v5.1
- P2 : profils matériel sauvegardés — v5.2
- P2 : filtres Kanban — v5.2
- P3 : amélioration regex wilaya — v5.3

# Ce que ce parcours prouve

- L'outil **s'adapte à un vrai métier** sans le réinventer
- Le **gain de temps est réel** et mesurable dès le 1er AO
- Les **règles d'audit** rattrapent des erreurs humaines coûteuses
- Le **parcours est guidé** sans être prescriptif (Brahim reste maître de ses décisions)
- La **documentation générée** est de qualité professionnelle, imprimable tel quel

Ce parcours est le modèle à reproduire pour les 3 autres pilotes Cas 1 (Kamel, Amine, Nadia, Omar).
