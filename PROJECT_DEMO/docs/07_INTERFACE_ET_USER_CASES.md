---
title: "SOUMISSION.DZ — Interface et cas d'usage"
subtitle: "SPA vanilla JS, 7 écrans, parcours des 3 profils, installateur desktop"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Vue d'ensemble

Deux interfaces coexistent :

1. **SPA Web** (`static/`) — l'interface principale pour tous les utilisateurs. Servie par FastAPI, accessible via navigateur à `http://127.0.0.1:8000` (pilote local) ou `https://app.soumission.dz` (prod).
2. **Installateur desktop PySide6** (`installer/`) — pour les pilotes locaux. Wizard d'installation + fenêtre de gestion du serveur local + system tray.

# SPA Web — 7 écrans

## Entrée — Login/Signup

- Trois onglets : Connexion, Inscription entreprise (Cas 1), Inscription cabinet (Cas 2)
- Validation Pydantic côté serveur retournée en clair, affichage inline
- Redirection automatique vers le dashboard après succès
- Pas de "Mot de passe oublié" en v5.0 (reporté v6, procédure manuelle en attendant)

## 1. Dashboard

Affichage contextuel selon le profil :

**Cas 1** : 5 KPIs en cards

- Nombre de documents au coffre
- Nombre d'alertes d'expiration (avec seuils 7j/15j/30j)
- Nombre de références
- Nombre d'AO actifs
- Nombre de factures émises

Tableau des alertes d'expiration en-dessous (documents qui vont expirer).

**Cas 2** : KPIs globaux cabinet + liste des entreprises du portefeuille avec compteurs individuels.

**Cas 3** : liste des missions en cours + métriques personnelles (note moyenne, nombre de missions terminées).

**Admin** : statistiques plateforme (nombre d'entreprises, de transactions, de tickets hotline ouverts).

## 2. Coffre-fort

- Liste des **15 types officiels** de documents (CNAS, CASNOS, CACOBATPH, NIF, NIS, RC, extrait de rôle, attestation fiscale, statuts, casier judiciaire, bilans, qualifications BTPH, etc.)
- Pour chaque type présent : filename, taille, date d'émission, date d'expiration, bouton Télécharger, bouton Supprimer
- Upload par glisser-déposer ou bouton "Choisir un fichier" (limite 25 Mo)
- **Alertes visuelles** : bordure rouge si expire dans < 7 j, orange si < 15 j, jaune si < 30 j
- Filtre par type de document

## 3. Références

- Tableau des marchés précédents (objet, maître d'ouvrage, année, montant DA, type travaux)
- CRUD complet
- Utilisé automatiquement dans le mémoire technique généré

## 4. AO — Appels d'offres

- Liste des AO en cours ou historiques
- Bouton "Importer PDF" : upload d'un AO au format PDF, extraction regex des champs (48 wilayas reconnues)
- Bouton "Nouvel AO" : formulaire manuel
- Pour chaque AO :
  - Consulter les détails
  - Lancer **l'audit** (25 règles pondérées, verdict par règle OK/warning/danger, score total sur 100)
  - Générer le **mémoire DOCX** (7 sections) + **3 formulaires** (engagement, probité, références)

### Écran Audit

- Score global sur 100 en gros
- Répartition : OK / warning / danger en compteurs colorés
- Liste des 25 règles avec verdict + message explicatif + suggestion d'action si KO
- Catégories : documents, qualification, finances, calendrier, cohérence

## 5. Chiffrage

Nouveau en v5.0, résout le chaînon manquant entre AO et dépôt. 3 onglets :

### 5a. Catalogue

- **35 articles BTPH** avec code, libellé, unité, prix min/moyen/max (fourchettes marché)
- Champ de recherche / filtrage en live
- Organisés par catégorie (terrassement, gros œuvre, VRD, électricité, plomberie, menuiserie, peinture, étanchéité)

### 5b. Simulateur

Tableau éditable ligne par ligne :

- Colonne article (dropdown depuis le catalogue)
- Colonne quantité
- Colonne prix proposé
- Colonne prix moyen du marché (automatique)
- Colonne écart % (automatique, coloré)
- Bouton "Simuler" calcule verdict par ligne : `ok` (proche du marché), `bas` (< marché -15 %), `haut` (> marché +15 %), `hors_fourchette` (> min-max)
- Total général + écart moyen du DQE

Export CSV du simulateur.

### 5c. Templates

- **5 templates de marchés** pré-remplis : ROUTES, BATIMENT_PUBLIC, VRD, LPP, HYDRAULIQUE
- Saisie d'un budget cible → recalcul proportionnel des quantités
- Export CSV

## 6. Kanban dossiers

- 4 colonnes : À faire, En cours, À valider, Terminé
- Chaque carte = 1 dossier (nom, étape actuelle, score audit, date cible)
- Workflow des étapes : profil → documents → audit → chiffrage → mémoire → vérification → dépôt
- Drag & drop entre colonnes (passage d'un statut à l'autre)
- Click sur carte : détail complet (cautions associées, soumission si déposée, historique)

## 7. Assistance (Cas 3)

Écran visible uniquement si le plan le permet (tous sauf ARTISAN).

- Catalogue des **7 prestations** avec code, libellé, description, prix HT, délai max
- Bouton "Demander cette prestation" → création d'une mission brouillon
- Section "Mes missions" : liste des missions en cours avec statut coloré
- Détail d'une mission : brief, assistant affecté, échanges messagerie, livrables si déposés

### Workflow Cas 3 dans l'UI

1. **Brouillon** : client rédige le brief, choisit la prestation. Bouton "Confirmer & envoyer" → facture TTC générée, en attente paiement.
2. **En attente paiement** : bouton "Payer" (Edahabia mock en v5.0). Paiement OK → affectation automatique d'un assistant disponible.
3. **En cours** : messagerie client ↔ assistant + journal d'actions de l'assistant. Bouton "Signer le mandat" si pas encore fait.
4. **Livrée** : assistant a déposé les livrables. Client les télécharge, bouton "Valider" (délai 5 j).
5. **Validée** : transaction clôturée, note et commentaire enregistrés, paiement assistant libéré.
6. **Contestée** : désaccord, escalade admin plateforme.

## 8. Facturation

Nouveau en v5.0 :

- **Plans** : tableau des 6 plans tarifaires, bouton "Souscrire mensuel" ou "Souscrire annuel (-10%)"
- **Mes abonnements** : liste avec statut, date de début, date de fin
- **Mes factures** : liste avec numéro, date, libellé, HT, TTC, statut ; bouton PDF, bouton Payer

Factures générées au format PDF conforme fiscalité DZ (mentions NIF, NIS, RC, RIB plateforme, TVA 19 %).

## Navigation

Barre du haut avec :

- Logo SOUMISSION.DZ
- Liens onglets : Dashboard, Coffre, Références, AO, Chiffrage, Dossiers, Assistance, Facturation
- Nom utilisateur + rôle + déconnexion

Responsive mobile : menu hamburger en-dessous de 768 px. Tableaux en scroll horizontal sur mobile.

# Installateur desktop

## Wizard 5 pages (premier lancement)

### Page 1 — Bienvenue

- Logo + texte explicatif : "Assistant d'installation de SOUMISSION.DZ v5.0"
- Bouton "Suivant"

### Page 2 — Vérification prérequis

- Auto-détection Python 3.11+
- Liste des dépendances Python requises avec statut coloré (installé / manquant)
- Bouton "Installer les dépendances manquantes" si nécessaire (subprocess pip)
- Bouton "Suivant" activé uniquement si tout est OK

### Page 3 — Configuration

- Dossier d'installation (par défaut `C:\Users\XXX\SOUMISSION.DZ` ou `~/SOUMISSION.DZ`)
- Port HTTP (par défaut 8000, détection auto si occupé)
- Case à cocher "Lancer au démarrage de Windows" (Windows uniquement)
- Case à cocher "Charger les données de démonstration" (recommandé pour la 1re utilisation)
- Bouton "Suivant"

### Page 4 — Installation

- Barre de progression
- Log scrollable avec les étapes : copie des fichiers, création `.env` avec JWT_SECRET aléatoire, `alembic upgrade head`, seeds démo optionnels
- Bouton "Suivant" activé en fin de traitement

### Page 5 — Terminé

- Message de succès
- Bouton "Lancer SOUMISSION.DZ maintenant" (démarre l'app et ouvre le navigateur)
- Bouton "Terminer"

## Fenêtre principale (après installation)

4 onglets :

### Onglet Statut

- Statut du serveur : colored dot + texte ("En marche sur http://127.0.0.1:8000" / "Arrêté")
- Boutons : Démarrer, Arrêter, Redémarrer, Ouvrir le navigateur
- Logs uvicorn en bas (dernières 100 lignes, scrollable, colorés)

### Onglet Sauvegardes

- Bouton "Créer une sauvegarde maintenant" → génère un ZIP horodaté dans `backups/`
- Liste des sauvegardes existantes (nom, date, taille) avec boutons : Restaurer, Supprimer
- Bouton "Ouvrir le dossier des sauvegardes"

### Onglet Paramètres

- Port HTTP (modifiable, redémarrage requis)
- Variable `SOUMISSION_ENV` (development / production)
- `LOG_LEVEL`
- Bouton "Régénérer JWT_SECRET" (déconnecte tous les utilisateurs actuels)
- Bouton "Lancer au démarrage" (Windows)
- Bouton "Réinitialiser (supprime tout)" — avec confirmation

### Onglet À propos

- Version v5.0
- Mentions légales (Belhof)
- Lien vers la doc utilisateur (PDF local)
- Lien vers le support (`support@soumission.dz`)
- Changelog condensé

## System tray

Icône drapeau algérien dans la barre système. Clic droit → menu :

- Ouvrir SOUMISSION.DZ (lance le navigateur)
- Ouvrir la fenêtre de gestion
- Démarrer / Arrêter (selon état)
- Quitter

Notifications natives OS pour les alertes critiques (erreur de démarrage, backup effectué).

# Parcours utilisateur type

## Brahim — Cas 1 (patron BTPH)

1. Reçoit le `.exe` par email, double-clique
2. Wizard installe en 3 min (dépendances incluses)
3. Compte créé depuis la SPA (`brahim@alpha-btph.dz`, SARL, wilaya 22, secteur BTPH, qualification IV)
4. Dashboard vierge → signup réussi, JWT stocké en session
5. Coffre : uploade CNAS, CASNOS, NIF, RC, qualification BTPH (15 min)
6. Références : saisit 5 marchés précédents (10 min)
7. Nouveau AO : importe un PDF reçu du MO → 80 % des champs remplis automatiquement
8. Lance l'audit : 88/100, quelques warnings → corrige ce qui manque
9. Chiffrage : importe le DQE depuis le template ROUTES, ajuste quantités, exporte CSV
10. Génère mémoire DOCX + 3 formulaires → ouvre dans Word, imprime, signe, dépose

Temps total pour préparer 1 AO : **2 h** vs 6-8 h en manuel.

## Mourad — Cas 2 (cabinet consultant)

1. Installation idem
2. Signup cabinet : nom "Cabinet Mourad Conseils", plan EXPERT
3. Ajoute 3 entreprises à son portefeuille (BatiWilaya, ElectroBourouba, AgroFournis)
4. Pour chacune : uploade les documents administratifs (1 h par entreprise la 1re fois)
5. AO entrants : sélectionne l'entreprise active via dropdown en haut de l'UI → travaille normalement
6. Fonctionnalité unique : **comparateur** → pour un AO, quel est le classement des 3 entreprises en termes d'éligibilité ? (scoring automatique basé sur qualifications, références, wilaya)
7. Facturation : reçoit une seule facture SOUMISSION.DZ au plan EXPERT

## Yacine — Cas 3 (assistant agréé)

1. Pas d'installation chez lui — il se connecte à la plateforme hébergée (mode 2 ou 3)
2. Dashboard : liste des missions à affecter (triées par prestation / plan de l'entreprise / urgence)
3. Prend une mission → mandat à signer électroniquement (coche + typing nom complet)
4. Reçoit les accès borés par le mandat (uniquement ce dossier, uniquement ces actions)
5. Travaille dans l'UI du client (coffre, références, AO, dossier) comme s'il était le client
6. Communique via messagerie intégrée
7. Livre (upload du mémoire finalisé) → statut passe à "livrée"
8. Client valide → note 5, paiement assistant libéré, mandat archivé

# Accessibilité

- Contrastes AA minimum sur tous les textes
- Navigation clavier complète (Tab, Enter, Escape)
- Labels `<label for="...">` sur tous les inputs
- Messages d'erreur associés aux champs (ARIA)
- Zoom jusqu'à 200 % sans perte

Pas de lecteur d'écran complet optimisé en v5.0 (reporté selon feedback).
