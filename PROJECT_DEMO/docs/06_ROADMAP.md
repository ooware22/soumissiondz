---
title: "SOUMISSION.DZ — Roadmap"
subtitle: "Actions post-v5.0, préparation v6, horizon 12 mois"
author: "Belhof — Fondateur"
date: "Avril 2026 — Version 5.0"
---

# Où en est-on ?

**v5.0 livrée et fonctionnelle.** Les 9 lots du mega-prompt sont implémentés, 110 tests pytest passent, la base de démonstration simule 2 mois d'activité réaliste. L'installateur desktop est prêt à être distribué aux 4 pilotes identifiés.

Le travail de développement v5.0 est **terminé**. Les prochaines étapes sont d'ordre commercial et opérationnel.

# Phase 1 — Signature des pilotes (semaines 1-4)

## Action concrète

Pour chacun des 4 pilotes identifiés, une LOI (Lettre d'Intention) avec :

- Engagement d'usage réel sur 8-12 semaines
- Accès gratuit pendant la période de pilote
- Engagement de retour hebdomadaire structuré (30 min / semaine)
- Possibilité de conversion en abonnement payant au tarif normal ensuite
- Confidentialité réciproque sur les données et les retours

## Livrables techniques associés

- Signer le `.exe` Windows avec un certificat code signing (évite SmartScreen)
- Créer une clé USB d'installation par pilote (backup si problème Internet)
- Documentation utilisateur papier 4 pages (imprimable) + PDF lisible

## Risques

- **Un pilote abandonne en cours de route** : prévoir un 5e pilote en backup (Nadia Omega Fournitures identifiée)
- **Un pilote rencontre un bug bloquant** : s'engager sur correction < 48 h avec `.exe` mis à jour envoyé

# Phase 2 — Exploitation pilote (semaines 5-16)

## Rituel hebdomadaire

Par pilote, 30 min de call structuré :

1. **Ce qui s'est passé** : combien d'AO traités, combien remportés, temps passé sur la plateforme
2. **Ce qui a marché** : fonctionnalités effectivement utilisées, temps gagné
3. **Ce qui a bloqué** : bugs, confusion UI, manque fonctionnel
4. **Demandes précises** : à noter dans un backlog priorisé

## Backlog des feedbacks

- Un fichier `FEEDBACK_PILOTES.md` dans le repo
- Une ligne par retour, format : `[Pilote] [Date] [Priorité P1/P2/P3] — Description`
- Revue hebdomadaire pour prioriser et affecter à une version (5.1, 5.2, 6.0)

## Métriques à collecter

- **Activation** : après combien de jours le pilote a uploadé son 1er document ? importé son 1er AO ? créé son 1er dossier complet ?
- **Engagement** : nombre de jours d'usage actif / semaine
- **Valeur perçue** : combien de temps économisé par AO (estimation pilote)
- **NPS qualitatif** : « recommanderais-tu à un confrère ? »

# Phase 3 — Itérations v5.x (semaines 6-16 en parallèle)

Versions mineures au fil du feedback :

## v5.1 — Corrections bloquantes (semaines 6-8)

- Bugs P1 remontés par pilotes
- Améliorations d'ergonomie (copie de dossier, presets pour AO récurrents)
- Notifications email sur alertes d'expiration documents (pas de push, simple SMTP)

## v5.2 — Ajustements métier (semaines 9-12)

- Nouveaux types de documents suite aux retours (ex. attestation sociale secteur privé, certificats qualité)
- Nouveaux templates de chiffrage sur demande pilote (ex. électricité, plomberie pure)
- Ajouts règles d'audit selon retours terrain

## v5.3 — Polish (semaines 13-16)

- Génération DOCX : améliorations de mise en page suite retours
- Export Excel du DQE en plus du CSV
- Améliorations du Kanban (filtres, tri)

# Phase 4 — Conversion pilotes en payant (semaines 12-16)

Décision go/no-go commerciale à la fin du pilote. Critères de succès :

- Au moins **3 des 4 pilotes** acceptent de passer en abonnement payant
- NPS moyen ≥ 7/10
- Gain de temps moyen perçu ≥ 30 % sur la préparation d'un dossier

Si go : facturation dès la semaine 17, pilotes facturés au tarif normal.

# Phase 5 — v6.0 (mois 5-8)

Développement majeur à condition que les pilotes convertissent. Thèmes :

## v6.0 — Scale et hébergement

- Passage en hébergement cloud Algérie (mode 3 du document 05)
- Migration à PostgreSQL obligatoire
- Mise en place monitoring (Sentry alternative, Prometheus)
- Plan de reprise d'activité (PRA)

## v6.0 — Paiement en ligne

- Intégration **Satim / Edahabia** réelle (mockée en v5.0)
- Spécifications Satim à obtenir (contrat commerçant + certification technique)
- Tests sandbox, puis production

## v6.0 — IA assistance à la rédaction

- Module IA pour **suggestions** dans le mémoire technique (non bloquant, désactivable)
- Classification automatique d'AO par catégorie et niveau de difficulté
- Note technique prédite vs historique
- Choix LLM à faire (open source pour souveraineté ? Claude API ? hybride ?)

## v6.0 — API publique et webhooks

- API publique documentée pour intégrations ERP comptabilité
- Webhooks sortants (ex. notification sur nouveau document expirant)
- Clés API par organisation, rotation gérée

## v6.0 — Mobile natif ou PWA

- Analyse besoin mobile après feedback pilote
- Si besoin confirmé : PWA d'abord (pas de store), app native si justifié

# Phase 6 — v7 et au-delà (mois 9+)

Hypothèses à tester :

- **Marketplace d'assistants** : ouvrir le Cas 3 à des assistants indépendants (pas seulement agréés plateforme), commission plateforme 15-20 %
- **Module formation** : capsules vidéo sur « comment répondre à un AO de routes », « comment chiffrer un LPP », monétisation par module
- **Intégration avec services e-gov DZ** : dépôt électronique des dossiers si le cadre réglementaire évolue (suivre les annonces ANPM)
- **Export Maghreb** : Maroc et Tunisie ont des marchés similaires avec adaptations (Maroc : Pharme, Tunisie : TUNEPS). Analyse d'opportunité seulement après succès stabilisé en Algérie.

# Risques identifiés et mitigations

| Risque                                        | Probabilité | Impact | Mitigation                                          |
| --------------------------------------------- | ----------- | ------ | --------------------------------------------------- |
| Concurrent local lance produit similaire      | Moyenne     | Élevé  | Vitesse d'exécution, premium en service pilote      |
| Évolution réglementaire marchés publics       | Moyenne     | Moyen  | Veille active, architecture modulaire sur formulaires |
| Un pilote abandonne sans feedback             | Moyenne     | Moyen  | Pilote backup en standby (Nadia Omega)              |
| Intégration Satim bloque 6 mois               | Élevée      | Moyen  | Garder mode "virement simple" en fallback           |
| Volume pilote dépasse SQLite                  | Faible      | Faible | Migration PostgreSQL déjà testée                    |
| Incident de sécurité (fuite données)          | Faible      | Élevé  | Checklist sécurité, audit externe v6                |
| Conformité ARPCE change                       | Moyenne     | Moyen  | Veille juridique, avocat conseil identifié          |

# KPIs pilotage

| Indicateur                                    | Cible v5   | Cible v6   |
| --------------------------------------------- | ---------- | ---------- |
| Pilotes signés                                | 4          | -          |
| Pilotes actifs hebdo                          | 3+         | -          |
| Pilotes convertis en payant                   | 3+         | -          |
| Entreprises payantes                          | 3-4        | 20-40      |
| MRR (Monthly Recurring Revenue)               | 30-40 kDA  | 200-400 kDA|
| Churn mensuel                                 | < 10 %     | < 5 %      |
| NPS                                           | ≥ 7        | ≥ 8        |
| Temps moyen préparation dossier (vs baseline) | -30 %      | -50 %      |
| Incidents de sécurité                         | 0          | 0          |

# Points de vigilance continue

- **Ne pas construire en avance** de feedback — chaque fonctionnalité v5.x doit venir d'un retour pilote précis
- **Ne pas fragmenter** l'architecture prématurément — rester monolithe tant que 1 seul serveur suffit
- **Ne pas négliger le support** — un pilote qui attend 48 h pour un bug lâche
- **Ne pas baisser la garde sur la sécurité** — les 4 garanties G1-G4 restent le socle
- **Ne pas renier les contraintes** — hébergement DZ, pas d'arabe, pas d'IA v5, fiscalité DZ respectée
