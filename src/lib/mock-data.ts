// ============================================================
// Soumission DZ - Mock data for frontend-only development
// Realistic Algerian business data matching PROJECT_DEMO
// ============================================================

import type {
  MeResponse, Document, DocumentType, AlerteExpiration,
  Reference, AppelOffres, AuditResult, PrixArticle,
  Template, ChiffrageResult, KanbanData, Prestation,
  Mission, Plan, Abonnement, Facture,
} from "@/lib/types";

// ---------- Users ----------
export const MOCK_USERS: Record<string, { password: string; me: MeResponse }> = {
  // --- Rôles Décisionnels & Globaux ---
  "patron@alpha-btph.dz": {
    password: "Demo12345",
    me: { id: 1, email: "patron@alpha-btph.dz", username: "Brahim (Patron)", role: "PATRON", organisation_id: 1, organisation_nom: "Alpha BTPH", organisation_type: "ENTREPRISE", plan_code: "PRO" },
  },
  "validateur@alpha-btph.dz": {
    password: "Demo12345",
    me: { id: 5, email: "validateur@alpha-btph.dz", username: "Karim (Validateur)", role: "VALIDATEUR", organisation_id: 1, organisation_nom: "Alpha BTPH", organisation_type: "ENTREPRISE", plan_code: "PRO" },
  },

  // --- Rôles Opérationnels (Cas 1) ---
  "chef_dossier@alpha-btph.dz": {
    password: "Demo12345",
    me: { id: 6, email: "chef_dossier@alpha-btph.dz", username: "Sara (Chef Dossier)", role: "CHEF_DOSSIER", organisation_id: 1, organisation_nom: "Alpha BTPH", organisation_type: "ENTREPRISE", plan_code: "PRO" },
  },
  "auditeur@alpha-btph.dz": {
    password: "Demo12345",
    me: { id: 7, email: "auditeur@alpha-btph.dz", username: "Yassine (Auditeur)", role: "AUDITEUR", organisation_id: 1, organisation_nom: "Alpha BTPH", organisation_type: "ENTREPRISE", plan_code: "PRO" },
  },
  "preparateur@alpha-btph.dz": {
    password: "Demo12345",
    me: { id: 8, email: "preparateur@alpha-btph.dz", username: "Amira (Préparateur)", role: "PREPARATEUR", organisation_id: 1, organisation_nom: "Alpha BTPH", organisation_type: "ENTREPRISE", plan_code: "PRO" },
  },
  "lecteur@alpha-btph.dz": {
    password: "Demo12345",
    me: { id: 9, email: "lecteur@alpha-btph.dz", username: "Comptable (Lecteur)", role: "LECTEUR", organisation_id: 1, organisation_nom: "Alpha BTPH", organisation_type: "ENTREPRISE", plan_code: "PRO" },
  },

  // --- Rôles Externes & Plateforme (Cas 2 & 3) ---
  "consultant@cabinet.dz": {
    password: "Demo12345",
    me: { id: 3, email: "consultant@cabinet.dz", username: "Mourad (Consultant)", role: "CONSULTANT", organisation_id: 3, organisation_nom: "Cabinet Mourad Conseils", organisation_type: "CABINET", plan_code: "EXPERT", cabinet_id: 1 },
  },
  "expert@soumission.dz": {
    password: "Demo12345",
    me: { id: 10, email: "expert@soumission.dz", username: "Expert (Assistance)", role: "ASSISTANT_AGREE", organisation_id: 4, organisation_nom: "Soumission DZ", organisation_type: "ENTREPRISE", plan_code: "EXPERT" },
  },
  "admin@soumission.dz": {
    password: "Admin12345",
    me: { id: 4, email: "admin@soumission.dz", username: "Admin (Plateforme)", role: "ADMIN_PLATEFORME", organisation_id: 4, organisation_nom: "Soumission DZ", organisation_type: "ENTREPRISE", plan_code: "EXPERT" },
  },
};

// ---------- Document types ----------
export const MOCK_DOC_TYPES: DocumentType[] = [
  { code: "RC", libelle: "Registre du commerce" },
  { code: "NIF", libelle: "Numéro d'identification fiscale" },
  { code: "NIS", libelle: "Numéro d'identification statistique" },
  { code: "CNAS", libelle: "Attestation CNAS" },
  { code: "CASNOS", libelle: "Attestation CASNOS" },
  { code: "CACOBATPH", libelle: "Attestation CACOBATPH" },
  { code: "EXTRAIT_ROLE", libelle: "Extrait de rôle" },
  { code: "CASIER", libelle: "Casier judiciaire" },
  { code: "BILANS", libelle: "Bilans comptables (3 ans)" },
  { code: "QUALIF", libelle: "Certificat de qualification" },
  { code: "REFERENCE_BONNE_EXEC", libelle: "Attestation de bonne exécution" },
  { code: "CAUTION_SOUMISSION", libelle: "Caution de soumission" },
  { code: "DECLARATION_PROBITE", libelle: "Déclaration de probité" },
  { code: "DECLARATION_CANDIDATURE", libelle: "Déclaration de candidature" },
  { code: "LETTRE_SOUMISSION", libelle: "Lettre de soumission" },
];

// ---------- Documents ----------
export const MOCK_DOCUMENTS: Document[] = [
  { id: 1, type_code: "RC", filename: "RC_Alpha_BTPH_2024.pdf", size_bytes: 245760, date_expiration: "2026-12-31", created_at: "2026-01-15T10:00:00Z" },
  { id: 2, type_code: "NIF", filename: "NIF_001234567890.pdf", size_bytes: 102400, created_at: "2026-01-15T10:05:00Z" },
  { id: 3, type_code: "CNAS", filename: "CNAS_Q1_2026.pdf", size_bytes: 184320, date_expiration: "2026-06-30", created_at: "2026-03-01T09:00:00Z" },
  { id: 4, type_code: "CASNOS", filename: "CASNOS_2026.pdf", size_bytes: 153600, date_expiration: "2026-05-15", created_at: "2026-02-20T11:30:00Z" },
  { id: 5, type_code: "CACOBATPH", filename: "CACOBATPH_Alpha.pdf", size_bytes: 204800, date_expiration: "2026-09-30", created_at: "2026-01-20T14:00:00Z" },
  { id: 6, type_code: "QUALIF", filename: "Qualification_Cat_III.pdf", size_bytes: 307200, date_expiration: "2027-03-15", created_at: "2026-01-10T08:00:00Z" },
  { id: 7, type_code: "BILANS", filename: "Bilans_2023_2024_2025.pdf", size_bytes: 1048576, created_at: "2026-02-01T09:30:00Z" },
  { id: 8, type_code: "EXTRAIT_ROLE", filename: "Extrait_Role_2026.pdf", size_bytes: 81920, date_expiration: "2026-04-30", created_at: "2026-03-15T10:00:00Z" },
];

// ---------- Alerts ----------
export const MOCK_ALERTES: AlerteExpiration[] = [
  { type_code: "EXTRAIT_ROLE", date_expiration: "2026-04-30", jours_restants: 12, seuil: "15j" },
  { type_code: "CASNOS", date_expiration: "2026-05-15", jours_restants: 27, seuil: "30j" },
  { type_code: "CNAS", date_expiration: "2026-06-30", jours_restants: 73, seuil: "30j" },
];

// ---------- References ----------
export const MOCK_REFERENCES: Reference[] = [
  { id: 1, objet: "Réalisation d'un bâtiment R+4 - Cité 500 logements", maitre_ouvrage: "OPGI Blida", annee: 2024, montant_da: 45000000, type_travaux: "Bâtiment", created_at: "2026-01-10" },
  { id: 2, objet: "Aménagement VRD lotissement El-Wouroud", maitre_ouvrage: "APC Boufarik", annee: 2023, montant_da: 18500000, type_travaux: "VRD", created_at: "2026-01-10" },
  { id: 3, objet: "Revêtement route CW14 - PK 12+300 au PK 18+700", maitre_ouvrage: "DTP Wilaya de Blida", annee: 2023, montant_da: 32000000, type_travaux: "Routes", created_at: "2026-01-10" },
  { id: 4, objet: "Construction école primaire - Commune de Chréa", maitre_ouvrage: "Direction de l'Éducation", annee: 2022, montant_da: 25000000, type_travaux: "Bâtiment", created_at: "2026-01-10" },
  { id: 5, objet: "Réseau AEP - Quartier Bab Essour", maitre_ouvrage: "ADE Blida", annee: 2024, montant_da: 12000000, type_travaux: "Hydraulique", created_at: "2026-02-15" },
];

// ---------- AO ----------
export const MOCK_AOS: AppelOffres[] = [
  { id: 1, reference: "AO-2026-042", objet: "Construction d'un complexe sportif de proximité - Blida", maitre_ouvrage: "DJS Wilaya de Blida", wilaya_code: "09", date_limite: "2026-05-15", budget_estime_da: 85000000, qualification_requise_cat: "Cat. III", created_at: "2026-03-20" },
  { id: 2, reference: "AO-2026-038", objet: "Réhabilitation du réseau d'assainissement - Centre-ville Médéa", maitre_ouvrage: "ONA Médéa", wilaya_code: "26", date_limite: "2026-05-01", budget_estime_da: 42000000, created_at: "2026-03-15" },
  { id: 3, reference: "AO-2026-055", objet: "Aménagement des espaces verts - Nouveau pôle urbain Bouinan", maitre_ouvrage: "DUAC Blida", wilaya_code: "09", date_limite: "2026-06-10", budget_estime_da: 15000000, created_at: "2026-04-01" },
  { id: 4, reference: "AO-2026-061", objet: "Réfection de la toiture et étanchéité - Lycée Ibn Khaldoun", maitre_ouvrage: "Direction de l'Éducation Alger", wilaya_code: "16", date_limite: "2026-04-28", budget_estime_da: 8500000, created_at: "2026-04-05" },
];

// ---------- Audit ----------
export const MOCK_AUDIT: AuditResult = {
  score: 72, verdict_global: "acceptable",
  total_ok: 16, total_warning: 6, total_danger: 3,
  regles: [
    { code: "R01", libelle: "Registre du commerce valide", categorie: "administratif", poids: 5, verdict: "ok", message: "RC présent et non expiré" },
    { code: "R02", libelle: "NIF fourni", categorie: "fiscal", poids: 5, verdict: "ok", message: "NIF disponible" },
    { code: "R03", libelle: "NIS fourni", categorie: "fiscal", poids: 3, verdict: "warning", message: "NIS non trouvé dans le coffre", action: "Uploader le NIS" },
    { code: "R04", libelle: "CNAS à jour", categorie: "social", poids: 5, verdict: "ok", message: "Attestation CNAS valide" },
    { code: "R05", libelle: "CASNOS à jour", categorie: "social", poids: 5, verdict: "warning", message: "Expire dans 27 jours", action: "Renouveler avant le 15/05" },
    { code: "R06", libelle: "CACOBATPH à jour", categorie: "social", poids: 4, verdict: "ok", message: "Attestation valide" },
    { code: "R07", libelle: "Extrait de rôle récent", categorie: "fiscal", poids: 4, verdict: "warning", message: "Expire dans 12 jours", action: "Renouveler d'urgence" },
    { code: "R08", libelle: "Casier judiciaire vierge", categorie: "administratif", poids: 5, verdict: "danger", message: "Casier non trouvé", action: "Obtenir un casier de moins de 3 mois" },
    { code: "R09", libelle: "Bilans comptables (3 ans)", categorie: "financier", poids: 5, verdict: "ok", message: "3 bilans disponibles" },
    { code: "R10", libelle: "Qualification professionnelle", categorie: "technique", poids: 5, verdict: "ok", message: "Cat. III - conforme" },
    { code: "R11", libelle: "Références similaires", categorie: "technique", poids: 5, verdict: "ok", message: "5 références trouvées" },
    { code: "R12", libelle: "Montant références ≥ AO", categorie: "technique", poids: 4, verdict: "ok", message: "Cumul 132.5M DA ≥ 85M DA" },
    { code: "R13", libelle: "Déclaration de probité", categorie: "administratif", poids: 3, verdict: "ok", message: "Modèle disponible" },
    { code: "R14", libelle: "Déclaration de candidature", categorie: "administratif", poids: 3, verdict: "ok", message: "Modèle disponible" },
    { code: "R15", libelle: "Lettre de soumission", categorie: "administratif", poids: 3, verdict: "ok", message: "Modèle disponible" },
    { code: "R16", libelle: "Caution de soumission (1-2%)", categorie: "financier", poids: 5, verdict: "danger", message: "Caution non trouvée (1.7M DA requis)", action: "Demander la caution à la banque" },
    { code: "R17", libelle: "DQE cohérent", categorie: "chiffrage", poids: 4, verdict: "warning", message: "DQE non encore soumis" },
    { code: "R18", libelle: "Date limite respectée", categorie: "délai", poids: 5, verdict: "ok", message: "27 jours restants" },
    { code: "R19", libelle: "Mémoire technique", categorie: "technique", poids: 4, verdict: "warning", message: "Non encore généré", action: "Générer le mémoire" },
    { code: "R20", libelle: "Planning des travaux", categorie: "technique", poids: 3, verdict: "warning", message: "Non fourni", action: "Préparer un planning" },
    { code: "R21", libelle: "Moyens humains", categorie: "technique", poids: 3, verdict: "ok", message: "Détail dans le mémoire" },
    { code: "R22", libelle: "Moyens matériels", categorie: "technique", poids: 3, verdict: "ok", message: "Détail dans le mémoire" },
    { code: "R23", libelle: "Conformité cahier des charges", categorie: "conformité", poids: 4, verdict: "ok", message: "Vérifié" },
    { code: "R24", libelle: "Timbre fiscal", categorie: "fiscal", poids: 2, verdict: "danger", message: "Non joint", action: "Joindre le timbre fiscal" },
    { code: "R25", libelle: "Signature et cachet", categorie: "administratif", poids: 3, verdict: "ok", message: "OK" },
  ],
};

// ---------- Prix articles ----------
export const MOCK_ARTICLES: PrixArticle[] = [
  { code: "GRO001", libelle: "Béton armé dosé à 350 kg/m³", categorie: "Gros œuvre", unite: "m³", prix_min_da: 22000, prix_moy_da: 26000, prix_max_da: 32000 },
  { code: "GRO002", libelle: "Maçonnerie en briques creuses", categorie: "Gros œuvre", unite: "m²", prix_min_da: 2200, prix_moy_da: 2800, prix_max_da: 3500 },
  { code: "GRO003", libelle: "Coffrage soigné", categorie: "Gros œuvre", unite: "m²", prix_min_da: 1800, prix_moy_da: 2400, prix_max_da: 3200 },
  { code: "VRD001", libelle: "Terrassement en pleine masse", categorie: "VRD", unite: "m³", prix_min_da: 800, prix_moy_da: 1200, prix_max_da: 1800 },
  { code: "VRD005", libelle: "Bordure de trottoir T2", categorie: "VRD", unite: "ml", prix_min_da: 1400, prix_moy_da: 1800, prix_max_da: 2200 },
  { code: "ETN001", libelle: "Étanchéité multicouche", categorie: "Étanchéité", unite: "m²", prix_min_da: 3500, prix_moy_da: 4200, prix_max_da: 5500 },
  { code: "RTE001", libelle: "Grave bitume 0/20", categorie: "Routes", unite: "tonne", prix_min_da: 8000, prix_moy_da: 9500, prix_max_da: 12000 },
  { code: "PLB001", libelle: "Tuyau PEHD DN110", categorie: "Plomberie", unite: "ml", prix_min_da: 2800, prix_moy_da: 3500, prix_max_da: 4200 },
  { code: "ELC001", libelle: "Câble U1000 RO2V 3×2.5", categorie: "Électricité", unite: "ml", prix_min_da: 350, prix_moy_da: 480, prix_max_da: 650 },
  { code: "PNT001", libelle: "Peinture vinylique 2 couches", categorie: "Peinture", unite: "m²", prix_min_da: 450, prix_moy_da: 650, prix_max_da: 900 },
];

// ---------- Templates ----------
export const MOCK_TEMPLATES: Template[] = [
  { code: "TPL_ROUTES", nom: "Routes et chaussées", budget_reference_da: 50000000 },
  { code: "TPL_BATIMENT", nom: "Bâtiment R+4 standard", budget_reference_da: 80000000 },
  { code: "TPL_VRD", nom: "VRD lotissement", budget_reference_da: 25000000 },
  { code: "TPL_LPP", nom: "Logement promotionnel public", budget_reference_da: 120000000 },
  { code: "TPL_HYDRAULIQUE", nom: "Réseau AEP", budget_reference_da: 35000000 },
];

// ---------- Kanban ----------
export const MOCK_KANBAN: KanbanData = {
  a_faire: [
    { id: 4, nom: "Lycée Ibn Khaldoun - Toiture", ao_id: 4, statut: "a_faire", etape_actuelle: "profil", created_at: "2026-04-05" },
  ],
  en_cours: [
    { id: 1, nom: "Complexe sportif Blida", ao_id: 1, statut: "en_cours", etape_actuelle: "chiffrage", score_audit: 72, created_at: "2026-03-20" },
    { id: 2, nom: "Assainissement Médéa", ao_id: 2, statut: "en_cours", etape_actuelle: "documents", score_audit: 58, created_at: "2026-03-15" },
  ],
  a_valider: [
    { id: 3, nom: "Espaces verts Bouinan", ao_id: 3, statut: "a_valider", etape_actuelle: "verification", score_audit: 89, created_at: "2026-04-01" },
  ],
  termine: [],
};

// ---------- Prestations ----------
export const MOCK_PRESTATIONS: Prestation[] = [
  { code: "PREP_DOSSIER", nom: "Préparation complète du dossier", description: "Montage intégral du dossier administratif et technique", prix_ht_da: 45000, delai_max_jours: 5 },
  { code: "AUDIT_DOCS", nom: "Audit documentaire", description: "Vérification exhaustive des documents et conformité", prix_ht_da: 15000, delai_max_jours: 2 },
  { code: "REDAC_MEMOIRE", nom: "Rédaction mémoire technique", description: "Rédaction professionnelle du mémoire technique adapté à l'AO", prix_ht_da: 35000, delai_max_jours: 3 },
  { code: "CHIFFRAGE_DQE", nom: "Chiffrage et DQE", description: "Élaboration du devis quantitatif estimatif complet", prix_ht_da: 25000, delai_max_jours: 3 },
  { code: "DEPOT_PHYSIQUE", nom: "Dépôt physique du dossier", description: "Impression, reliure et dépôt au lieu indiqué", prix_ht_da: 8000, delai_max_jours: 1 },
  { code: "PACK_COMPLET", nom: "Pack complet (tout inclus)", description: "De l'audit au dépôt, prestation clé en main", prix_ht_da: 95000, delai_max_jours: 7 },
  { code: "CONSEIL_STRATEGIE", nom: "Conseil stratégique AO", description: "Analyse de l'AO et recommandations de positionnement", prix_ht_da: 20000, delai_max_jours: 2 },
];

// ---------- Missions ----------
export const MOCK_MISSIONS: Mission[] = [
  { id: 1, prestation_code: "AUDIT_DOCS", statut: "validee", brief: "Audit complet des documents pour AO complexe sportif", prix_ttc_da: 17850, created_at: "2026-03-22T10:00:00Z" },
  { id: 2, prestation_code: "REDAC_MEMOIRE", statut: "en_cours", brief: "Rédaction mémoire technique AO assainissement Médéa", prix_ttc_da: 41650, created_at: "2026-04-10T14:00:00Z" },
  { id: 3, prestation_code: "CHIFFRAGE_DQE", statut: "brouillon", brief: "Chiffrage DQE pour espaces verts Bouinan", prix_ttc_da: 29750, created_at: "2026-04-15T09:00:00Z" },
];

// ---------- Plans ----------
export const MOCK_PLANS: Plan[] = [
  { code: "DECOUVERTE", nom: "Découverte", prix_mensuel_da: 0, prix_annuel_da: 0 },
  { code: "ARTISAN", nom: "Artisan", prix_mensuel_da: 5000, prix_annuel_da: 54000 },
  { code: "PRO", nom: "Pro", prix_mensuel_da: 10000, prix_annuel_da: 108000 },
  { code: "BUSINESS", nom: "Business", prix_mensuel_da: 15000, prix_annuel_da: 162000 },
  { code: "EXPERT", nom: "Expert", prix_mensuel_da: 20000, prix_annuel_da: 216000 },
  { code: "HOTLINE", nom: "Hotline", prix_mensuel_da: 3000, prix_annuel_da: 32400 },
];

// ---------- Abonnements ----------
export const MOCK_ABONNEMENTS: Abonnement[] = [
  { id: 1, plan_code: "PRO", periodicite: "mensuel", debut: "2026-03-01", fin: "2026-04-01", statut: "actif", montant_da: 10000 },
];

// ---------- Factures ----------
export const MOCK_FACTURES: Facture[] = [
  { id: 1, numero: "SDZ-2026-00001", date_emission: "2026-03-01", libelle: "Abonnement Pro - Mars 2026", prix_ht_da: 8403, prix_ttc_da: 10000, statut: "payee" },
  { id: 2, numero: "SDZ-2026-00002", date_emission: "2026-03-22", libelle: "Mission AUDIT_DOCS #1", prix_ht_da: 15000, prix_ttc_da: 17850, statut: "payee" },
  { id: 3, numero: "SDZ-2026-00003", date_emission: "2026-04-01", libelle: "Abonnement Pro - Avril 2026", prix_ht_da: 8403, prix_ttc_da: 10000, statut: "emise" },
  { id: 4, numero: "SDZ-2026-00004", date_emission: "2026-04-10", libelle: "Mission REDAC_MEMOIRE #2", prix_ht_da: 35000, prix_ttc_da: 41650, statut: "emise" },
];

// ---------- Cautions ----------
export const MOCK_CAUTIONS: any[] = [
  { id: 1, ao_id: 1, ao_objet: "Complexe sportif Blida", type: "soumission", montant_da: 1700000, banque: "CPA", date_emission: "2026-04-01", date_expiration: "2026-07-01", statut: "active" },
  { id: 2, ao_id: 2, ao_objet: "Assainissement Médéa", type: "bonne_execution", montant_da: 2100000, banque: "BEA", date_emission: "2025-10-15", statut: "active" },
];

// ---------- Soumissions History ----------
export const MOCK_SOUMISSIONS: any[] = [
  { id: 1, ao_id: 101, ao_objet: "Rénovation école primaire", date_depot: "2025-11-20", montant_soumis_da: 24500000, rang: 2, statut: "eliminee", ecart_pct: 12 },
  { id: 2, ao_id: 102, ao_objet: "Construction de 50 logts", date_depot: "2026-01-15", montant_soumis_da: 125000000, rang: 1, statut: "retenue", ecart_pct: -3 },
  { id: 3, ao_id: 103, ao_objet: "Aménagement voirie", date_depot: "2026-03-05", montant_soumis_da: 32000000, statut: "deposee" },
];

// ---------- Cabinet Portfolio ----------
export const MOCK_CABINET_ENTREPRISES: any[] = [
  { id: 1, nom: "Alpha BTPH", nif: "00123456789", nb_documents: 8, nb_ao_actifs: 2, nb_alertes: 3, score_dernier_audit: 72 },
  { id: 2, nom: "Batipro Sétif", nif: "00987654321", nb_documents: 15, nb_ao_actifs: 5, nb_alertes: 0, score_dernier_audit: 95 },
  { id: 3, nom: "EURL Construction Moderne", nb_documents: 3, nb_ao_actifs: 0, nb_alertes: 5 },
];

// ---------- Team ----------
export const MOCK_TEAM: any[] = [
  { id: 1, username: "Brahim", email: "brahim@alpha-btph.dz", role: "PATRON", actif: true, created_at: "2025-01-10T08:00:00Z" },
  { id: 2, username: "Karim", email: "karim@alpha-btph.dz", role: "CHEF_DOSSIER", actif: true, created_at: "2025-02-15T09:30:00Z" },
  { id: 3, username: "Samir", email: "samir@alpha-btph.dz", role: "PREPARATEUR", actif: false, created_at: "2025-06-20T14:15:00Z" },
];

// ---------- Hotline ----------
export const MOCK_TICKETS: any[] = [
  { id: 1, sujet: "Problème d'importation PDF", message: "Le fichier de l'AO de la wilaya 09 n'est pas reconnu.", priorite: "haute", statut: "ouvert", created_at: "2026-04-18T08:30:00Z" },
  { id: 2, sujet: "Question sur le chiffrage", message: "Comment ajouter un nouvel article dans le DQE ?", priorite: "moyenne", statut: "resolu", reponse: "Vous pouvez ajouter des postes personnalisés via l'interface Chiffrage.", created_at: "2026-04-10T10:00:00Z" },
];

// ---------- Parrainage ----------
export const MOCK_PARRAINAGE: any = {
  code: "SDZ-A1B2C3D4",
  nb_filleuls: 3,
  commission_totale_da: 15000,
};

// ---------- Admin Stats ----------
export const MOCK_ADMIN_STATS: any = {
  total_entreprises: 145,
  total_cabinets: 12,
  total_users: 350,
  total_ao: 850,
  total_dossiers: 1200,
  total_missions: 45,
  revenus_mois_da: 850000,
  revenus_total_da: 12500000,
};

export const MOCK_ADMIN_USERS: any[] = [
  { id: 1, username: "Brahim", email: "brahim@alpha-btph.dz", role: "PATRON", organisation_nom: "Alpha BTPH", organisation_type: "ENTREPRISE", plan_code: "PRO", actif: true, created_at: "2025-01-10" },
  { id: 2, username: "Kamel", email: "kamel@batipro-setif.dz", role: "PATRON", organisation_nom: "Batipro Sétif", organisation_type: "ENTREPRISE", plan_code: "BUSINESS", actif: true, created_at: "2025-03-20" },
  { id: 3, username: "Mourad", email: "mourad@cabinet-mourad.dz", role: "CONSULTANT", organisation_nom: "Cabinet Mourad Conseils", organisation_type: "CABINET", plan_code: "EXPERT", actif: true, created_at: "2025-05-15" },
];
