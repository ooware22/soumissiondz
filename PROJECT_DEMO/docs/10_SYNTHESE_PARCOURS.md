---
title: "SOUMISSION.DZ — Synthèse des parcours"
subtitle: "Comparaison des 3 cas d'usage, matrice fonctionnelle, décisions rapides"
author: "Équipe SOUMISSION.DZ"
date: "Avril 2026 — Version 5.0"
---

# Objectif

Ce document est un **résumé visuel** des 3 parcours utilisateur, destiné à :

- L'équipe commerciale pour identifier rapidement le cas d'usage d'un prospect
- L'équipe support pour router un ticket vers le bon expert
- Les rédacteurs de documentation pour aligner les exemples

# Tableau comparatif

| Dimension                    | Cas 1 — Entreprise autonome        | Cas 2 — Cabinet consultant        | Cas 3 — Assistance plateforme       |
| ---------------------------- | ---------------------------------- | --------------------------------- | ----------------------------------- |
| **Profil**                   | PME 5-100 employés                 | Consultant indépendant / cabinet  | Tout Cas 1 ou Cas 2 en surcharge    |
| **Exemple prospect**         | Brahim (Alpha BTPH, SBA)           | Mourad (Cabinet Alger)            | Yacine (assistant interne)          |
| **Relation à la plateforme** | Utilisateur direct                 | Utilisateur direct + agrégateur   | Prestataire payé à l'acte           |
| **Organisation technique**   | 1 Org + 1 Entreprise + N Users     | 1 Org CABINET + N Entreprises     | Assistant dans Org Plateforme       |
| **Scoping**                  | `organisation_id = ctx.org_id`     | `cabinet_id` + header entreprise  | `Mandat` signé avec périmètre borné |
| **Plan tarifaire cible**     | ARTISAN / PRO / BUSINESS           | EXPERT                            | N/A (pas d'abonnement)              |
| **Prix mensuel**             | 5 000 / 10 000 / 15 000 DA         | 20 000 DA                         | Commission 30 % sur prestations     |
| **Nombre d'utilisateurs**    | 1 à illimité selon plan            | 1-2 consultants                   | 1 assistant par mission             |
| **Signup self-service**      | Oui                                | Oui                               | **Non — recrutement admin**         |
| **Fonctionnalités uniques**  | Coffre, audit, chiffrage, mémoire  | Comparateur portefeuille          | Mandat, messagerie, journal actions |
| **Facturation**              | Facture mensuelle unique           | Facture unique EXPERT             | Facturation à l'acte par prestation |
| **Livrables**                | Mémoire DOCX + 3 formulaires       | Idem + tableau comparatif         | Idem, produit par l'assistant       |
| **Onboarding**               | 5 tâches J+14                      | Idem + import des N entreprises   | Charte + formation 1 h              |

# Matrice fonctionnelle — Qui peut faire quoi

| Fonctionnalité                            | Cas 1 Patron | Cas 1 Chef | Cas 1 Aud. | Cas 2 Consultant | Cas 3 Assistant | Admin |
| ----------------------------------------- | :----------: | :--------: | :--------: | :--------------: | :-------------: | :---: |
| Signup entreprise                         | ✓            | ✗          | ✗          | ✗                | ✗               | ✗     |
| Signup cabinet                            | ✗            | ✗          | ✗          | ✓                | ✗               | ✗     |
| Ajouter entreprise au portefeuille        | ✗            | ✗          | ✗          | ✓                | ✗               | ✗     |
| Inviter un utilisateur                    | ✓            | ✗          | ✗          | ✓                | ✗               | ✓     |
| Recruter un assistant                     | ✗            | ✗          | ✗          | ✗                | ✗               | ✓     |
| Uploader documents coffre                 | ✓            | ✓          | ✗          | ✓                | ✓ (si mandat)   | ✗     |
| Créer / modifier référence                | ✓            | ✓          | ✗          | ✓                | ✓ (si mandat)   | ✗     |
| Importer AO PDF                           | ✓            | ✓          | ✗          | ✓                | ✓ (si mandat)   | ✗     |
| Lancer audit 25 règles                    | ✓            | ✓          | ✓          | ✓                | ✓ (si mandat)   | ✗     |
| Utiliser simulateur prix / templates      | ✓            | ✓          | ✓          | ✓                | ✓ (si mandat)   | ✗     |
| Générer mémoire DOCX                      | ✓            | ✓          | ✗          | ✓                | ✓ (si mandat)   | ✗     |
| Avancer un dossier dans le kanban         | ✓            | ✓          | ✗          | ✓                | ✓ (si mandat)   | ✗     |
| Enregistrer une caution                   | ✓            | ✓          | ✗          | ✓                | ✓ (si mandat)   | ✗     |
| Clôturer une soumission                   | ✓            | ✗          | ✗          | ✓                | ✗               | ✗     |
| Comparer les entreprises du portefeuille  | ✗            | ✗          | ✗          | ✓                | ✗               | ✗     |
| Demander une prestation Cas 3             | ✓            | ✓          | ✗          | ✓                | ✗               | ✗     |
| Accepter une mission Cas 3                | ✗            | ✗          | ✗          | ✗                | ✓               | ✗     |
| Valider une mission livrée                | ✓            | ✓          | ✗          | ✓                | ✗               | ✗     |
| Consulter plans tarifaires                | ✓            | ✓          | ✓          | ✓                | ✓               | ✓     |
| Souscrire un abonnement                   | ✓            | ✗          | ✗          | ✓                | ✗               | ✗     |
| Télécharger facture PDF                   | ✓            | ✗          | ✗          | ✓                | ✓ (ses missions)| ✓     |
| Configurer code de parrainage             | ✓            | ✗          | ✗          | ✓                | ✓               | ✗     |
| Ouvrir ticket hotline                     | ✓            | ✓          | ✓          | ✓                | ✓               | ✗     |
| Répondre ticket hotline                   | ✗            | ✗          | ✗          | ✗                | ✗               | ✓     |
| Exporter données loi 18-07                | ✓            | ✗          | ✗          | ✓                | ✗               | ✗     |
| Supprimer son compte                      | ✓            | ✗          | ✗          | ✓                | ✗               | ✗     |

Légende : ✓ = permis, ✗ = refusé (403 ou 404 selon visibilité)

# Décisions rapides

## "Quel plan recommander à ce prospect ?"

```
Questions :
├─ Combien d'entreprises à gérer ?
│  ├─ 1 seule
│  │  ├─ Combien d'employés ?
│  │  │  ├─ 1-5       → ARTISAN (5 000 DA)
│  │  │  ├─ 5-30      → PRO (10 000 DA)
│  │  │  └─ 30+       → BUSINESS (15 000 DA)
│  └─ Plusieurs (cabinet) → EXPERT (20 000 DA)
└─ Besoin de support renforcé ?
   └─ Ajouter HOTLINE (+4 000 DA)
```

## "Est-ce que ce prospect peut utiliser le Cas 3 ?"

Oui si et seulement si :

- Il a un compte Cas 1 ou Cas 2 actif (plan ≥ ARTISAN)
- Il accepte de payer à l'acte (prestation HT + TVA 19 %)
- Il accepte de signer un mandat électronique borné en temps et en périmètre

## "Quelle information remonte dans le dashboard ?"

| Profil   | KPIs affichés                                                            |
| -------- | ------------------------------------------------------------------------ |
| Cas 1    | Docs coffre, alertes expiration, références, AO actifs, factures         |
| Cas 2    | Idem pour chaque entreprise + vue agrégée du portefeuille                |
| Cas 3    | Missions en cours, note moyenne, nombre missions terminées               |
| Admin    | Nb entreprises, transactions, tickets ouverts, assistants actifs         |

## "Quels écrans sont visibles selon le plan ?"

| Plan       | Dashboard | Coffre | Refs | AO | Chiffrage | Dossiers | Assistance | Facturation |
| ---------- | :-------: | :----: | :--: | :-: | :-------: | :------: | :--------: | :---------: |
| DECOUVERTE | ✓         | ✓      | ✓    | ✓   | ✓         | ✓        | ✗          | ✓           |
| ARTISAN    | ✓         | ✓      | ✓    | ✓   | ✓         | ✓        | ✗          | ✓           |
| PRO        | ✓         | ✓      | ✓    | ✓   | ✓         | ✓        | ✓          | ✓           |
| BUSINESS   | ✓         | ✓      | ✓    | ✓   | ✓         | ✓        | ✓          | ✓           |
| EXPERT     | ✓         | ✓      | ✓    | ✓   | ✓         | ✓        | ✓          | ✓           |

# Flux de revenus

```
┌─────────────────────────────────────────────────────┐
│ Revenus récurrents (MRR)                            │
│ - Abonnements mensuels / annuels                    │
│ - 5 000 à 20 000 DA/mois × N entreprises            │
│ - Add-on HOTLINE 4 000 DA/mois                      │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│ Revenus à l'acte                                    │
│ - Mode sans abonnement 5 000 DA/dossier             │
│ - Commission Cas 3 30 % sur prestations             │
│   (8 000 à 95 000 DA HT par prestation)             │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│ Coûts                                               │
│ - Paiement assistants Cas 3 (70 % du HT)            │
│ - Hébergement cloud Algérie (~30 000 DA/mois)       │
│ - Support (heures Belhof + freelance)               │
│ - Marketing bouche à oreille (0 coût direct)        │
└─────────────────────────────────────────────────────┘
```

# Parcours-type en une phrase

- **Cas 1** : « Brahim ouvre SOUMISSION.DZ, importe son AO, l'outil extrait les champs et lui dit 88/100 avec 2 warnings ; il corrige, chiffre, génère le DOCX, dépose. »
- **Cas 2** : « Mourad ouvre la plateforme, bascule sur l'entreprise X de son portefeuille, fait le travail comme pour son propre compte ; en fin de mois il reçoit une seule facture SOUMISSION.DZ pour les 3 entreprises. »
- **Cas 3** : « Brahim a un AO urgent, demande URGENCE_72H, paie 113 050 DA TTC, signe le mandat, Yacine traite, livre sous 72 h, Brahim valide et Yacine est payé. »

# Erreurs fréquentes à éviter

- **Confondre Cas 2 et Cas 3.** Cas 2 = consultant qui gère N entreprises sous abonnement. Cas 3 = assistant qui intervient ponctuellement via mandat.
- **Recommander EXPERT à une entreprise seule.** EXPERT = cabinet. Pour 1 entreprise grosse, BUSINESS suffit.
- **Proposer Cas 3 à un compte DECOUVERTE.** Nécessite un plan payant actif.
- **Penser que l'assistant Cas 3 voit tout.** Il voit uniquement ce que le mandat autorise, sur la durée spécifiée.
