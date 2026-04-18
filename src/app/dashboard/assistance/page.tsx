"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";
import { formatDA, cn } from "@/lib/utils";
import type { Prestation, Mission } from "@/lib/types";
import { Headphones, ShoppingCart, Clock, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

const STATUT_CFG: Record<string, { label: string; color: string; bg: string }> = {
  brouillon: { label: "Brouillon", color: "text-muted", bg: "bg-zinc-800" },
  en_attente_paiement: { label: "Paiement", color: "text-warning", bg: "bg-warning-muted" },
  en_cours: { label: "En cours", color: "text-accent", bg: "bg-accent-muted" },
  livree: { label: "Livrée", color: "text-sky-400", bg: "bg-sky-500/10" },
  validee: { label: "Validée", color: "text-success", bg: "bg-success-muted" },
  contestee: { label: "Contestée", color: "text-danger", bg: "bg-danger-muted" },
};

export default function AssistancePage() {
  const [prestations, setPrestations] = useState<Prestation[]>([]);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [ordering, setOrdering] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiGet<Prestation[]>("/assistance/prestations").catch(() => []),
      apiGet<Mission[]>("/missions").catch(() => []),
    ]).then(([p, m]) => { setPrestations(p); setMissions(m); setLoading(false); });
  }, []);

  const handleOrder = async (code: string) => {
    setOrdering(code);
    try {
      const m = await apiPost<Mission>("/missions", { prestation_code: code, brief: "Demande depuis le dashboard" });
      setMissions([m, ...missions]);
    } catch { /* */ }
    setOrdering(null);
  };

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-20 w-full" />)}</div>;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
          <Headphones className="h-6 w-6 text-pink-400" />Assistance & Hotline
        </h1>
        <p className="mt-1 text-sm text-muted">Commandez des prestations d&apos;accompagnement professionnel.</p>
      </div>

      {/* Catalog */}
      <div>
        <h2 className="text-sm font-semibold mb-3">Catalogue de prestations</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {prestations.map(p => (
            <div key={p.code} className="rounded-xl border border-border bg-card p-5 flex flex-col justify-between hover:border-border-hover transition-colors">
              <div>
                <h3 className="font-semibold text-sm">{p.nom}</h3>
                <p className="mt-1 text-xs text-muted leading-relaxed">{p.description}</p>
                <div className="mt-3 flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{p.delai_max_jours}j max</span>
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between">
                <span className="text-lg font-bold text-accent">{formatDA(p.prix_ht_da)}<span className="text-xs text-muted-foreground font-normal"> HT</span></span>
                <button onClick={() => handleOrder(p.code)} disabled={ordering === p.code} className="flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-xs font-medium text-white transition-all hover:bg-accent-hover disabled:opacity-50 active:scale-[0.98]">
                  {ordering === p.code ? <Loader2 className="h-3 w-3 animate-spin" /> : <ShoppingCart className="h-3 w-3" />}
                  Commander
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Missions */}
      {missions.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold mb-3">Vos missions</h2>
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-border text-left">
                {["#", "Prestation", "Brief", "Montant", "Statut"].map(h => (
                  <th key={h} className="px-5 py-3 text-xs font-medium uppercase tracking-wider text-muted-foreground">{h}</th>
                ))}
              </tr></thead>
              <tbody>{missions.map(m => {
                const s = STATUT_CFG[m.statut] || STATUT_CFG.brouillon;
                return (
                  <tr key={m.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                    <td className="px-5 py-3 font-mono text-xs text-accent">#{m.id}</td>
                    <td className="px-5 py-3 font-medium">{m.prestation_code}</td>
                    <td className="px-5 py-3 text-muted max-w-[200px] truncate">{m.brief || "-"}</td>
                    <td className="px-5 py-3">{m.prix_ttc_da ? formatDA(m.prix_ttc_da) : "-"}</td>
                    <td className="px-5 py-3">
                      <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium", s.bg, s.color)}>
                        {m.statut === "validee" ? <CheckCircle2 className="h-3 w-3" /> : m.statut === "contestee" ? <AlertCircle className="h-3 w-3" /> : null}
                        {s.label}
                      </span>
                    </td>
                  </tr>
                );
              })}</tbody>
            </table>
          </div>
          </div>
        </div>
      )}
    </div>
  );
}
