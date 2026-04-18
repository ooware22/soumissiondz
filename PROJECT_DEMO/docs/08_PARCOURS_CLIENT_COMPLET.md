---
title: "SOUMISSION.DZ — Parcours client complet"
subtitle: "De la découverte à la fidélisation, flux end-to-end"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Objectif du document

Ce document détaille le parcours complet d'un client de SOUMISSION.DZ, depuis le premier contact jusqu'à la fidélisation long terme, en passant par l'usage quotidien. Il s'adresse autant à l'équipe commerciale qu'à l'équipe produit.

# Étape 0 — Découverte

## Canaux de découverte

- **Bouche à oreille** dans les milieux BTPH et études (prospection initiale faite par Belhof auprès de 10 contacts)
- **Salons professionnels** : Batimatec (Alger), salon de l'entreprise algérienne
- **Presse professionnelle** : articles dans magazines techniques (Journal du BTP DZ, etc.)
- **Réseau consultants** : un consultant Cas 2 recommande à plusieurs de ses clients
- **Référencement web** (mineur en v5.0, à renforcer en v6)

## Premier contact

Le prospect visite `soumission.dz` (site vitrine, hors périmètre v5.0 technique) ou est contacté en direct. Il demande une démonstration.

## Démonstration

30-45 minutes en présentiel ou visio, scénario type :

1. Connexion avec le compte démo `brahim@alpha-btph.dz` — 1 min
2. Dashboard pré-rempli : 4 AO, 14 documents, 3 alertes → l'outil "parle tout seul"
3. Tour du coffre-fort : "voici toutes les pièces que l'administration va demander"
4. Import d'un vrai AO du prospect depuis son PDF → extraction automatique des champs
5. Lancement de l'audit : 25 règles, score, détection des risques → "vous auriez raté ça"
6. Chiffrage : simulateur de prix avec verdicts fourchettes marché
7. Génération du mémoire DOCX : ouvert dans Word pour montrer le résultat
8. Facturation et plans : comparaison des 6 niveaux, recommandation selon taille

Sortie : demande d'essai sur LOI (pilote gratuit 8-12 semaines) ou engagement direct au tarif.

# Étape 1 — Signup et onboarding

## Création de compte

### Cas 1 — Entreprise autonome

Formulaire (UI `/signup/entreprise`) :

- Email professionnel + mot de passe + confirmation
- Nom de l'entreprise, forme juridique (SARL/SPA/EURL/SNC/ETI/AUTO-ENTREPRENEUR)
- NIF, NIS, RC
- Wilaya (liste déroulante 48 wilayas)
- Adresse, téléphone
- Secteur, activité, effectif, CA moyen
- Qualification si BTPH (catégorie + date d'expiration)
- Checkbox CGU et consentement loi 18-07 (obligatoires)

Backend :

- Validation Pydantic (email valide, mots de passe ≥ 8 caractères, NIF 15 chiffres)
- Création `Organisation` type=ENTREPRISE avec plan par défaut DECOUVERTE (14 j gratuit)
- Création `Entreprise` liée
- Création `User` role=PATRON avec `consent_at=now()`
- Génération JWT et retour au client

### Cas 2 — Cabinet consultant

Formulaire (UI `/signup/cabinet`) :

- Email, mot de passe
- Nom du cabinet, nom du consultant principal
- NIF du cabinet, wilaya, téléphone

Backend similaire : création `Organisation` type=CABINET, `Cabinet`, `User` role=CONSULTANT.

Le consultant ajoute ensuite N entreprises dans son portefeuille via `POST /cabinet/entreprises`.

### Cas 3 — Assistant agréé

**Pas de self-service.** Le recrutement passe par l'admin plateforme :

1. Candidature spontanée (mail `jobs@soumission.dz` ou formulaire site vitrine)
2. Entretien + vérification pièces (CV, références, pièce d'identité)
3. Signature de la charte (doc PDF, contre-signé par admin)
4. Admin crée manuellement le compte via `POST /admin/assistants` avec spécialités, IBAN
5. Assistant reçoit ses accès par email

## Onboarding semaine 1

Liste de checks accessibles depuis le dashboard ("Bienvenue, voici vos prochaines étapes") :

- [ ] Compléter le profil entreprise (tous les champs)
- [ ] Uploader **au moins 10 documents** au coffre (CNAS, CASNOS, NIF, NIS, RC, statuts, casier, bilans)
- [ ] Saisir **au moins 3 références** de marchés précédents
- [ ] Inviter un 2e utilisateur (chef de dossier)
- [ ] Choisir un plan ≥ ARTISAN pour continuer après 14 jours

Email de relance automatique à J+7 et J+12 si l'un des 5 items manque.

# Étape 2 — Usage quotidien

## Cycle type d'un AO

### Jour 0 — Réception de l'AO

Le patron ou le chef de dossier reçoit l'AO par :

- PDF du maître d'ouvrage en pièce jointe
- Téléchargement depuis la plateforme officielle (ANPM, journaux)
- Courrier papier numérisé

Action dans SOUMISSION.DZ :

1. Ouvre l'écran **AO**
2. Clique "Importer PDF"
3. Upload → extraction automatique (référence, objet, MO, wilaya, date limite, budget, qualification requise)
4. Vérification visuelle des champs extraits, correction si besoin
5. Enregistrement

### Jour 1 — Décision "on y va ou pas"

L'entreprise lance **l'audit** de l'AO :

- 25 règles évaluées (voir document 03 section rules_engine)
- Score 0-100
- Répartition OK / warning / danger

Si score < 50 ou plus de 3 dangers critiques : l'entreprise **passe son tour** (évite des frais de dossier inutiles).

Si score ≥ 70 : décision "on prépare le dossier", création d'un **Dossier** au statut "À faire".

### Jours 2-7 — Préparation du dossier

Workflow en 7 étapes (visibles dans le Kanban) :

1. **profil** — vérifier que les données entreprise sont à jour
2. **documents** — vérifier que tous les documents administratifs exigés par l'AO sont au coffre et non expirés
3. **audit** — consolider le résultat de l'audit, traiter les warnings
4. **chiffrage** — construire le DQE avec le simulateur de prix + templates
5. **memoire** — générer le mémoire technique DOCX, l'adapter manuellement
6. **verification** — revue finale par le patron, dernière passe
7. **depot** — préparer les 3 formulaires officiels, imprimer, signer, déposer physiquement

Chaque transition met à jour `etape_actuelle` du dossier.

### Jour J-1 — Dernière vérification

- Tous les documents sont imprimés
- Tous les formulaires sont signés
- La caution de soumission (1 % du budget) est obtenue de la banque
- Le dossier est organisé selon l'ordre exigé par le CPT

### Jour J — Dépôt

- Dépôt physique au siège du MO (la plupart des AO DZ sont encore papier en 2026)
- Accusé de réception obtenu
- Saisie dans SOUMISSION.DZ : `POST /dossiers/{id}/deposer` avec date et numéro d'AR

Le statut du dossier passe à "Terminé" et une ligne **Soumission** est créée avec `date_depot`.

### Jours J+30 à J+90 — Attente du résultat

- Séance d'ouverture des plis (J+15 à J+30 généralement)
- Analyse des offres par la commission (J+30 à J+60)
- Notification au candidat retenu (J+60 à J+90)

### Jour d'attribution

Saisie du résultat dans SOUMISSION.DZ :

- Si **gagné** : mise à jour `Soumission.statut=gagne`, `rang=1`, `montant_attributaire_da=...`. Déclenchement des actions post-attribution (caution bonne exécution 5 %, enregistrement comme référence).
- Si **perdu** : `statut=perdu`, `rang=X`, `raison_libre="Prix plus élevé que l'attributaire"`. La caution de soumission peut être récupérée.

## Cycle de facturation SOUMISSION.DZ

Chaque mois (ou chaque année selon périodicité) :

1. Facture générée automatiquement (jour d'anniversaire de l'abonnement)
2. Email envoyé au client avec la facture PDF en pièce jointe
3. Client paie via Edahabia (mock en v5.0, réel en v6) ou virement bancaire
4. Statut `emise` → `payee` avec `paiement_recu_at`

Relances automatiques :

- J+5 après échéance : rappel
- J+10 : 2e rappel
- J+15 : suspension du compte (statut `impaye`)
- J+30 : résiliation de l'abonnement

## Usage Cas 2 (cabinet)

Le consultant opère sur N entreprises. Workflow spécifique :

- Selector en haut de l'UI pour changer d'entreprise active
- Dashboard cabinet : vue globale portefeuille (KPIs agrégés)
- **Comparateur** : pour un AO donné, montre le classement des entreprises du portefeuille
- Facturation unique au plan EXPERT (commission sur les LOI gagnées possible en v6)

## Usage Cas 3 (assistance ponctuelle)

Un client entreprise (Cas 1 ou Cas 2) qui manque de temps :

1. Ouvre l'écran **Assistance**
2. Choisit une des 7 prestations (ex. REDACTION_MEMOIRE à 25 000 DA HT)
3. Rédige le brief (texte libre expliquant l'AO, les spécificités, les deadlines)
4. Confirme → facture TTC générée
5. Paie → un assistant disponible est affecté (par spécialité et charge)
6. Signe le mandat (checkbox + saisie nom complet)
7. Échange messagerie avec l'assistant si besoin
8. Récupère les livrables (mémoire rédigé, formulaires pré-remplis)
9. Valide ou conteste sous 5 jours

# Étape 3 — Fidélisation et expansion

## Parrainage

Chaque utilisateur dispose d'un code de parrainage personnel visible dans son profil.

- Si un filleul s'inscrit avec ce code et passe à un plan payant
- Le parrain reçoit **20 % de commission** sur les paiements du filleul pendant 12 mois
- Commission créditée chaque mois dans un "compte SOUMISSION.DZ" du parrain
- Retrait mensuel vers IBAN (modèle Satim à implémenter en v6)

## Hotline

Plan HOTLINE add-on (4 000 DA/mois) :

- Ticketing catégorisé en 3 niveaux : technique, conseil, expertise
- Délai de réponse garanti : 24 h (technique), 48 h (conseil), 72 h (expertise)
- Tickets tracés dans `TicketHotline`, historique consultable

## Upgrade de plan

Quand l'entreprise grossit :

- De ARTISAN à PRO (plus d'utilisateurs, plus d'AO)
- De PRO à BUSINESS (multi-utilisateurs étendu, priorité support)
- Migration en self-service depuis `/facturation/abonnements` (proratisation automatique)

## Hommes clés à surveiller

| Profil              | Besoins spécifiques                                     | Actions                                   |
| ------------------- | ------------------------------------------------------- | ----------------------------------------- |
| Patron BTPH         | Gain de temps, fiabilité, gestion multi-dossiers        | Plan PRO, formation à l'audit             |
| Chef de dossier     | Outils de collaboration, notifications                  | Plan BUSINESS (multi-user)                |
| Consultant cabinet  | Vision portefeuille, comparateur, facture unique        | Plan EXPERT, démo du comparateur          |
| Assistant agréé     | Flux de missions régulier, paiement fiable              | Recrutement, charte, paiement rapide      |

# Étape 4 — Fin de cycle

## Résiliation

- Self-service depuis `/facturation/abonnements/{id}/resilier`
- Prend effet à la fin de la période en cours
- Données conservées en base pendant 5 ans (loi 18-07 sur archivage fiscal)
- Possibilité de réactiver le compte avant J+90

## Suppression du compte (loi 18-07)

- Endpoint `DELETE /confidentialite/compte` (voir document 04)
- Soft-delete immédiat, purge physique J+30
- Export ZIP préalable proposé à l'utilisateur

## Rachat concurrent / consolidation

Pas de scénario immédiat en v5.0. Si un concurrent veut intégrer SOUMISSION.DZ à son offre, l'export ZIP permet la migration sortante facile (pas de lock-in des données).

# Métriques du parcours client

| Étape                           | Métrique clé                 | Cible v5 pilote |
| ------------------------------- | ---------------------------- | --------------- |
| Découverte → démo               | Taux de RDV démo             | 40 %            |
| Démo → signup                   | Taux de conversion           | 50 %            |
| Signup → onboarding complété    | Taux à J+14                  | 70 %            |
| Onboarding → 1er AO traité      | Délai moyen                  | 20 jours        |
| AO traité → AO gagné            | Taux de gain                 | 30-40 %         |
| Pilote gratuit → abonnement     | Taux de conversion           | 75 %            |
| Abonnement → rétention 6 mois   | Taux                         | > 85 %          |
| NPS promoteurs (note ≥ 9)       | Taux                         | ≥ 40 %          |
