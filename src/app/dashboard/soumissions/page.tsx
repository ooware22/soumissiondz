"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { formatDA, formatDateShort, cn } from "@/lib/utils";
import type { Soumission } from "@/lib/types";
import { History, TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function SoumissionsPage() {
  const [soumissions, setSoumissions] = useState<Soumission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<Soumission[]>("/soumissions").then(setSoumissions).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-16 w-full" />)}</div>;

  const retenues = soumissions.filter(s => s.statut === "retenue").length;
  const total = soumissions.length;
  const succesRate = total > 0 ? Math.round((retenues / total) * 100) : 0;

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><History className="h-6 w-6 text-purple-400" />Historique des soumissions</h1>
        <p className="mt-1 text-sm text-muted">Suivez vos statistiques de réussite et analysez vos écarts de prix.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-5 flex items-center justify-between">
          <div><h3 className="text-sm font-medium text-muted">Soumissions</h3><p className="mt-2 text-2xl font-bold">{total}</p></div>
        </div>
        <div className="rounded-xl border border-border bg-card p-5 flex items-center justify-between">
          <div><h3 className="text-sm font-medium text-muted">Retenues</h3><p className="mt-2 text-2xl font-bold text-success">{retenues}</p></div>
        </div>
        <div className="rounded-xl border border-border bg-card p-5 flex items-center justify-between">
          <div><h3 className="text-sm font-medium text-muted">Taux de succès</h3><p className="mt-2 text-2xl font-bold">{succesRate}%</p></div>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
          <thead><tr className="border-b border-border text-left">
            {["AO / Projet", "Date dépôt", "Montant soumis", "Écart (Moins disant)", "Rang", "Statut"].map(h => <th key={h} className="px-5 py-3 text-xs font-medium uppercase text-muted-foreground">{h}</th>)}
          </tr></thead>
          <tbody>{soumissions.map(s => (
            <tr key={s.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
              <td className="px-5 py-3 font-medium">{s.ao_objet}</td>
              <td className="px-5 py-3 text-muted">{formatDateShort(s.date_depot)}</td>
              <td className="px-5 py-3">{formatDA(s.montant_soumis_da)}</td>
              <td className="px-5 py-3">
                {s.ecart_pct !== undefined && (
                  <span className={cn("flex items-center gap-1 font-medium", s.ecart_pct > 0 ? "text-danger" : s.ecart_pct < 0 ? "text-success" : "text-muted")}>
                    {s.ecart_pct > 0 ? <TrendingUp className="h-3 w-3" /> : s.ecart_pct < 0 ? <TrendingDown className="h-3 w-3" /> : <Minus className="h-3 w-3" />}
                    {s.ecart_pct > 0 ? "+" : ""}{s.ecart_pct}%
                  </span>
                )}
              </td>
              <td className="px-5 py-3 font-medium text-accent">{s.rang ? `#${s.rang}` : "-"}</td>
              <td className="px-5 py-3 capitalize">
                <span className={cn("px-2.5 py-0.5 rounded-full text-xs font-medium", s.statut === "retenue" ? "bg-success-muted text-success" : s.statut === "eliminee" ? "bg-danger-muted text-danger" : "bg-surface text-muted")}>
                  {s.statut}
                </span>
              </td>
            </tr>
          ))}</tbody>
        </table>
          </div>
      </div>
    </div>
  );
}
