// ============================================================
// Soumission DZ - TypeScript domain types
// Mirrors the FastAPI Pydantic schemas from PROJECT_DEMO
// ============================================================

// ---------- Auth ----------
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface MeResponse {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  organisation_id: number;
  organisation_nom: string;
  organisation_type: OrgType;
  plan_code: PlanCode;
  cabinet_id?: number;
}

// ---------- Enums ----------
export type OrgType = "ENTREPRISE" | "CABINET";
export type OrgStatut = "actif" | "suspendu" | "impaye";
export type PlanCode =
  | "DECOUVERTE"
  | "ARTISAN"
  | "PRO"
  | "BUSINESS"
  | "EXPERT"
  | "HOTLINE";
export type UserRole =
  | "PATRON"
  | "CHEF_DOSSIER"
  | "AUDITEUR"
  | "LECTEUR"
  | "VALIDATEUR"
  | "PREPARATEUR"
  | "CONSULTANT"
  | "ASSISTANT_AGREE"
  | "ADMIN_PLATEFORME";

// ---------- Signup ----------
export interface SignupEntrepriseRequest {
  nom_entreprise: string;
  forme_juridique?: string;
  email: string;
  username: string;
  password: string;
  telephone?: string;
}

export interface SignupCabinetRequest {
  nom_cabinet: string;
  consultant_principal: string;
  email: string;
  username: string;
  password: string;
}

// ---------- Coffre ----------
export interface DocumentType {
  code: string;
  libelle: string;
}

export interface Document {
  id: number;
  type_code: string;
  filename: string;
  size_bytes: number;
  date_emission?: string;
  date_expiration?: string;
  created_at: string;
}

export interface AlerteExpiration {
  type_code: string;
  date_expiration: string;
  jours_restants: number;
  seuil: "7j" | "15j" | "30j" | "expire";
}

// ---------- Références ----------
export interface Reference {
  id: number;
  objet: string;
  maitre_ouvrage?: string;
  annee?: number;
  montant_da?: number;
  type_travaux?: string;
  created_at: string;
}

export interface ReferenceCreate {
  objet: string;
  maitre_ouvrage?: string;
  annee?: number;
  montant_da?: number;
  type_travaux?: string;
}

// ---------- AO ----------
export interface AppelOffres {
  id: number;
  reference?: string;
  objet: string;
  maitre_ouvrage?: string;
  wilaya_code?: string;
  date_limite?: string;
  budget_estime_da?: number;
  qualification_requise_cat?: string;
  created_at: string;
}

export interface AoCreate {
  reference?: string;
  objet: string;
  maitre_ouvrage?: string;
  wilaya_code?: string;
  date_limite?: string;
  budget_estime_da?: number;
  qualification_requise_cat?: string;
}

// ---------- Audit ----------
export interface AuditResult {
  score: number;
  verdict_global: string;
  total_ok: number;
  total_warning: number;
  total_danger: number;
  regles: AuditRegle[];
}

export interface AuditRegle {
  code: string;
  libelle: string;
  categorie: string;
  poids: number;
  verdict: "ok" | "warning" | "danger";
  message: string;
  action?: string;
}

// ---------- Prix ----------
export interface PrixArticle {
  code: string;
  libelle: string;
  categorie: string;
  unite: string;
  prix_min_da: number;
  prix_moy_da: number;
  prix_max_da: number;
}

export interface SimulationPoste {
  article_code: string;
  quantite: number;
  prix_propose_da: number;
}

export interface SimulationResult {
  postes: SimulationPosteResult[];
  montant_total_propose_da: number;
  montant_total_reference_da: number;
  ecart_global_pct: number;
}

export interface SimulationPosteResult {
  article_code: string;
  libelle: string;
  quantite: number;
  prix_propose_da: number;
  prix_moy_da: number;
  ecart_vs_moy_pct: number;
  verdict: "ok" | "bas" | "haut" | "hors_fourchette";
}

// ---------- Templates ----------
export interface Template {
  code: string;
  nom: string;
  budget_reference_da: number;
}

export interface ChiffrageResult {
  code: string;
  nom: string;
  budget_cible_da: number;
  montant_calcule_da: number;
  postes: ChiffragePoste[];
}

export interface ChiffragePoste {
  article_code: string;
  libelle: string;
  unite: string;
  quantite: number;
  prix_unitaire_da: number;
  total_da: number;
}

// ---------- Dossiers ----------
export type DossierStatut = "a_faire" | "en_cours" | "a_valider" | "termine";
export type DossierEtape =
  | "profil"
  | "documents"
  | "audit"
  | "chiffrage"
  | "memoire"
  | "verification"
  | "depot";

export interface Dossier {
  id: number;
  nom: string;
  ao_id: number;
  statut: DossierStatut;
  etape_actuelle: DossierEtape;
  score_audit?: number;
  date_cible?: string;
  created_at: string;
}

export type KanbanData = Record<string, Dossier[]>;

// ---------- Assistance ----------
export interface Prestation {
  code: string;
  nom: string;
  description: string;
  prix_ht_da: number;
  delai_max_jours: number;
}

export type MissionStatut =
  | "brouillon"
  | "en_attente_paiement"
  | "en_cours"
  | "livree"
  | "validee"
  | "contestee";

export interface Mission {
  id: number;
  prestation_code: string;
  statut: MissionStatut;
  brief?: string;
  prix_ttc_da?: number;
  created_at: string;
}

// ---------- Billing ----------
export interface Plan {
  code: PlanCode;
  nom: string;
  prix_mensuel_da: number;
  prix_annuel_da: number;
}

export interface Abonnement {
  id: number;
  plan_code: PlanCode;
  periodicite: "mensuel" | "annuel";
  debut: string;
  fin?: string;
  statut: string;
  montant_da: number;
}

export interface Facture {
  id: number;
  numero: string;
  date_emission: string;
  libelle: string;
  prix_ht_da: number;
  prix_ttc_da: number;
  statut: "emise" | "payee";
}

// ---------- Cautions (Lot 4) ----------
export type CautionType = "soumission" | "bonne_execution" | "retenue_garantie";
export interface Caution {
  id: number;
  ao_id: number;
  ao_objet: string;
  type: CautionType;
  montant_da: number;
  banque: string;
  date_emission: string;
  date_expiration?: string;
  statut: "active" | "liberee" | "saisie";
}

// ---------- Soumissions History (Lot 4) ----------
export interface Soumission {
  id: number;
  ao_id: number;
  ao_objet: string;
  date_depot: string;
  montant_soumis_da: number;
  rang?: number;
  statut: "deposee" | "retenue" | "eliminee" | "infructueux";
  ecart_pct?: number;
}

// ---------- Cabinet (Lot 5) ----------
export interface CabinetEntreprise {
  id: number;
  nom: string;
  nif?: string;
  nb_documents: number;
  nb_ao_actifs: number;
  nb_alertes: number;
  score_dernier_audit?: number;
}

// ---------- Team (Lot 1) ----------
export interface TeamMember {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  actif: boolean;
  created_at: string;
}

// ---------- Hotline (Lot 7) ----------
export type TicketPriorite = "basse" | "moyenne" | "haute";
export interface Ticket {
  id: number;
  sujet: string;
  message: string;
  priorite: TicketPriorite;
  statut: "ouvert" | "en_cours" | "resolu" | "ferme";
  reponse?: string;
  created_at: string;
}

// ---------- Parrainage (Lot 7) ----------
export interface Parrainage {
  code: string;
  nb_filleuls: number;
  commission_totale_da: number;
}

// ---------- Admin (Lot 9) ----------
export interface AdminStats {
  total_entreprises: number;
  total_cabinets: number;
  total_users: number;
  total_ao: number;
  total_dossiers: number;
  total_missions: number;
  revenus_mois_da: number;
  revenus_total_da: number;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  organisation_nom: string;
  organisation_type: OrgType;
  plan_code: PlanCode;
  actif: boolean;
  created_at: string;
}
