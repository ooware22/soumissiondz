// ============================================================
// Soumission DZ - Mock API handler
// Intercepts all API calls and returns mock data
// Toggle: set USE_MOCK=false to use real backend
// ============================================================

import * as M from "@/lib/mock-data";
import type { MeResponse, SimulationResult } from "@/lib/types";
import { sleep } from "@/lib/utils";

export const USE_MOCK = true;

let currentUser: MeResponse | null = null;

// Simulate network delay
const delay = () => sleep(300 + Math.random() * 400);

type MockHandler = (body?: unknown) => Promise<unknown>;

const routes: Record<string, Record<string, MockHandler>> = {
  "POST /auth/login": {
    handler: async (body) => {
      const { email, password } = body as { email: string; password: string };
      const user = M.MOCK_USERS[email];
      if (!user || user.password !== password) throw new Error("Email ou mot de passe incorrect");
      currentUser = user.me;
      return { access_token: "mock_jwt_token_" + Date.now(), token_type: "bearer" };
    },
  },
  "GET /auth/me": {
    handler: async () => {
      if (!currentUser) throw new Error("Non authentifié");
      return currentUser;
    },
  },
  "POST /signup/entreprise": {
    handler: async (body) => {
      const b = body as Record<string, string>;
      currentUser = {
        id: 99, email: b.email, username: b.username, role: "PATRON",
        organisation_id: 99, organisation_nom: b.nom_entreprise,
        organisation_type: "ENTREPRISE", plan_code: "DECOUVERTE",
      };
      return { access_token: "mock_jwt_signup_" + Date.now(), token_type: "bearer" };
    },
  },
  "POST /signup/cabinet": {
    handler: async (body) => {
      const b = body as Record<string, string>;
      currentUser = {
        id: 98, email: b.email, username: b.username, role: "CONSULTANT",
        organisation_id: 98, organisation_nom: b.nom_cabinet,
        organisation_type: "CABINET", plan_code: "DECOUVERTE", cabinet_id: 98,
      };
      return { access_token: "mock_jwt_cab_" + Date.now(), token_type: "bearer" };
    },
  },
  "GET /coffre/types": { handler: async () => M.MOCK_DOC_TYPES },
  "GET /coffre/documents": { handler: async () => M.MOCK_DOCUMENTS },
  "GET /coffre/alertes": { handler: async () => M.MOCK_ALERTES },
  "POST /coffre/documents": {
    handler: async () => {
      return { id: 100, type_code: "RC", filename: "uploaded.pdf", size_bytes: 100000, created_at: new Date().toISOString() };
    },
  },
  "GET /references": { handler: async () => M.MOCK_REFERENCES },
  "POST /references": {
    handler: async (body) => {
      const b = body as Record<string, unknown>;
      return { id: M.MOCK_REFERENCES.length + 1, ...b, created_at: new Date().toISOString() };
    },
  },
  "GET /ao": { handler: async () => M.MOCK_AOS },
  "POST /ao": {
    handler: async (body) => {
      const b = body as Record<string, unknown>;
      return { id: M.MOCK_AOS.length + 1, ...b, created_at: new Date().toISOString() };
    },
  },
  "POST /ao/import-pdf": {
    handler: async () => ({
      id: 10, reference: "AO-2026-EXT", objet: "AO importé depuis PDF",
      champs_extraits: ["objet", "maitre_ouvrage", "wilaya_code", "date_limite"],
    }),
  },
  "GET /prix/articles": { handler: async () => M.MOCK_ARTICLES },
  "POST /prix/simuler": {
    handler: async (body) => {
      const { postes } = body as { postes: { article_code: string; quantite: number; prix_propose_da: number }[] };
      let totalPropose = 0, totalRef = 0;
      const results = postes.map((p) => {
        const art = M.MOCK_ARTICLES.find((a) => a.code === p.article_code);
        const moy = art?.prix_moy_da || p.prix_propose_da;
        const ecart = Math.round(((p.prix_propose_da - moy) / moy) * 100);
        totalPropose += p.prix_propose_da * p.quantite;
        totalRef += moy * p.quantite;
        return {
          article_code: p.article_code, libelle: art?.libelle || p.article_code,
          quantite: p.quantite, prix_propose_da: p.prix_propose_da, prix_moy_da: moy,
          ecart_vs_moy_pct: ecart,
          verdict: Math.abs(ecart) < 10 ? "ok" : Math.abs(ecart) < 25 ? (ecart > 0 ? "haut" : "bas") : "hors_fourchette",
        };
      });
      const result: SimulationResult = {
        postes: results as SimulationResult["postes"],
        montant_total_propose_da: totalPropose,
        montant_total_reference_da: totalRef,
        ecart_global_pct: Math.round(((totalPropose - totalRef) / totalRef) * 100),
      };
      return result;
    },
  },
  "GET /templates": { handler: async () => M.MOCK_TEMPLATES },
  "GET /dossiers/kanban": { handler: async () => M.MOCK_KANBAN },
  "GET /assistance/prestations": { handler: async () => M.MOCK_PRESTATIONS },
  "GET /missions": { handler: async () => M.MOCK_MISSIONS },
  "POST /missions": {
    handler: async (body) => {
      const b = body as Record<string, unknown>;
      return { id: 10, statut: "brouillon", ...b, prix_ttc_da: 0, created_at: new Date().toISOString() };
    },
  },
  "GET /plans": { handler: async () => M.MOCK_PLANS },
  "GET /abonnements": { handler: async () => M.MOCK_ABONNEMENTS },
  "GET /factures": { handler: async () => M.MOCK_FACTURES },
  "POST /abonnements": {
    handler: async (body) => {
      const b = body as Record<string, unknown>;
      return { id: 10, ...b, debut: new Date().toISOString().slice(0, 10), statut: "actif", montant_da: 10000 };
    },
  },
  "GET /cautions": { handler: async () => M.MOCK_CAUTIONS },
  "GET /soumissions": { handler: async () => M.MOCK_SOUMISSIONS },
  "GET /cabinet/entreprises": { handler: async () => M.MOCK_CABINET_ENTREPRISES },
  "GET /team": { handler: async () => M.MOCK_TEAM },
  "GET /hotline": { handler: async () => M.MOCK_TICKETS },
  "GET /parrainage/mon-code": { handler: async () => M.MOCK_PARRAINAGE },
  "GET /admin/stats": { handler: async () => M.MOCK_ADMIN_STATS },
  "GET /admin/users": { handler: async () => M.MOCK_ADMIN_USERS },
};

export async function mockApi<T>(path: string, opts: { method?: string; body?: unknown } = {}): Promise<T> {
  await delay();
  const method = opts.method || "GET";

  // Handle dynamic routes like /ao/1/audit, /factures/1/payer, etc.
  let routeKey = `${method} ${path}`;

  // Check exact match first
  if (routes[routeKey]) {
    return routes[routeKey].handler(opts.body) as Promise<T>;
  }

  // Dynamic route matching
  if (/^GET \/ao\/\d+\/audit$/.test(routeKey)) return M.MOCK_AUDIT as T;
  if (/^DELETE \/coffre\/documents\/\d+$/.test(routeKey)) return null as T;
  if (/^DELETE \/references\/\d+$/.test(routeKey)) return null as T;
  if (/^POST \/missions\/\d+\/signer-mandat$/.test(routeKey)) return { statut: "en_cours" } as T;
  if (/^POST \/missions\/\d+\/valider$/.test(routeKey)) return { statut: "validee" } as T;
  if (/^POST \/factures\/\d+\/payer$/.test(routeKey)) return { statut: "payee" } as T;
  if (/^POST \/templates\/[\w]+\/chiffrer$/.test(routeKey)) {
    const b = opts.body as { budget_cible_da: number };
    const code = path.split("/")[2];
    const tpl = M.MOCK_TEMPLATES.find((t) => t.code === code) || M.MOCK_TEMPLATES[0];
    const ratio = b.budget_cible_da / tpl.budget_reference_da;
    return {
      code: tpl.code, nom: tpl.nom, budget_cible_da: b.budget_cible_da,
      montant_calcule_da: Math.round(b.budget_cible_da * 0.97),
      postes: M.MOCK_ARTICLES.slice(0, 5).map((a) => ({
        article_code: a.code, libelle: a.libelle, unite: a.unite,
        quantite: Math.round(100 * ratio), prix_unitaire_da: a.prix_moy_da,
        total_da: Math.round(100 * ratio * a.prix_moy_da),
      })),
    } as T;
  }

  console.warn(`[MockAPI] No handler for: ${routeKey}`);
  return null as T;
}

// Set current user from stored session
export function mockSetUser(me: MeResponse | null) {
  currentUser = me;
}
