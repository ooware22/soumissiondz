"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";
import { formatDA, formatDateShort, cn } from "@/lib/utils";
import type { Caution } from "@/lib/types";
import { ShieldCheck, Plus, CheckCircle2, AlertCircle } from "lucide-react";

export default function CautionsPage() {
  const [cautions, setCautions] = useState<Caution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<Caution[]>("/cautions").then(setCautions).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="skeleton h-16 w-full" />)}</div>;

  const getStatut = (c: Caution) => {
    if (c.statut === "active") return { label: "Active", bg: "bg-success-muted", color: "text-success", icon: CheckCircle2 };
    if (c.statut === "liberee") return { label: "Libérée", bg: "bg-surface", color: "text-muted", icon: CheckCircle2 };
    return { label: "Saisie", bg: "bg-danger-muted", color: "text-danger", icon: AlertCircle };
  };

  const totalActif = cautions.filter(c => c.statut === "active").reduce((s, c) => s + c.montant_da, 0);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2"><ShieldCheck className="h-6 w-6 text-sky-400" />Cautions</h1>
          <p className="mt-1 text-sm text-muted">Gérez vos cautions bancaires (soumission, exécution, garantie).</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-all hover:bg-accent-hover">
          <Plus className="h-4 w-4" />Ajouter
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="text-sm font-medium text-muted">Total des cautions actives</h3>
          <p className="mt-2 text-2xl font-bold text-accent">{formatDA(totalActif)}</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-5">
          <h3 className="text-sm font-medium text-muted">Cautions à libérer (≤ 30j)</h3>
          <p className="mt-2 text-2xl font-bold">0</p>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
            <table className="w-full text-sm">
          <thead><tr className="border-b border-border text-left">
            {["Type", "AO / Marché", "Banque", "Montant", "Date émission", "Statut"].map(h => <th key={h} className="px-5 py-3 text-xs font-medium uppercase text-muted-foreground">{h}</th>)}
          </tr></thead>
          <tbody>{cautions.map(c => {
            const st = getStatut(c);
            return (
              <tr key={c.id} className="border-b border-border/50 last:border-0 hover:bg-card-hover transition-colors">
                <td className="px-5 py-3 font-medium capitalize">{c.type.replace("_", " ")}</td>
                <td className="px-5 py-3 text-muted">{c.ao_objet}</td>
                <td className="px-5 py-3 font-medium">{c.banque}</td>
                <td className="px-5 py-3">{formatDA(c.montant_da)}</td>
                <td className="px-5 py-3 text-muted">{formatDateShort(c.date_emission)}</td>
                <td className="px-5 py-3">
                  <span className={cn("inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium", st.bg, st.color)}>
                    <st.icon className="h-3 w-3" />{st.label}
                  </span>
                </td>
              </tr>
            );
          })}</tbody>
        </table>
          </div>
      </div>
    </div>
  );
}
